'''

Create an unified test_stub to share test operations

@author: Quarkonics
'''
import os
import random
import zstackwoodpecker.test_util  as test_util
import zstackwoodpecker.zstack_test.zstack_test_volume as zstack_volume_header
import zstackwoodpecker.zstack_test.zstack_test_security_group as zstack_sg_header
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.zstack_test.zstack_test_image as test_image
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.account_operations as acc_ops
import zstackwoodpecker.operations.datamigrate_operations as datamigr_ops
import zstackwoodpecker.operations.longjob_operations as longjob_ops
import zstackwoodpecker.operations.volume_operations as vol_ops
import zstackwoodpecker.operations.nas_operations as nas_ops
import zstackwoodpecker.operations.hybrid_operations as hyb_ops
import zstackwoodpecker.operations.primarystorage_operations as ps_ops
import zstackwoodpecker.operations.backupstorage_operations as bs_ops
import zstackwoodpecker.zstack_test.zstack_test_vm as test_vm_header
from zstackwoodpecker.test_chain import TestChain
import zstackwoodpecker.header.host as host_header
import zstacklib.utils.jsonobject as jsonobject
import zstackwoodpecker.test_state as test_state
from zstacklib.utils import shell
import threading
import time
import sys
import commands
import subprocess
#import traceback

hybrid_test_stub = test_lib.lib_get_test_stub('hybrid')


def create_vm(vm_name, image_name, l3_name):
    vm_creation_option = test_util.VmOption()
    image_uuid = test_lib.lib_get_image_by_name(image_name).uuid
    l3_net_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
    conditions = res_ops.gen_query_conditions('type', '=', 'UserVm')
    instance_offering_uuid = res_ops.query_resource(res_ops.INSTANCE_OFFERING, conditions)[0].uuid
    vm_creation_option.set_l3_uuids([l3_net_uuid])
    vm_creation_option.set_image_uuid(image_uuid)
    vm_creation_option.set_instance_offering_uuid(instance_offering_uuid)
    vm_creation_option.set_name(vm_name)
    vm = test_vm_header.ZstackTestVm()
    vm.set_creation_option(vm_creation_option)
    vm.create()
    return vm

def migrate_vm_to_differnt_cluster(vm):
    test_util.test_dsc("migrate vm to different cluster")
    if not test_lib.lib_check_vm_live_migration_cap(vm.vm):
        test_util.test_skip('skip migrate if live migrate not supported')

    current_host = test_lib.lib_find_host_by_vm(vm.vm)
    conditions = res_ops.gen_query_conditions('clusterUuid', '!=', current_host.clusterUuid)
    candidate_hosts = res_ops.query_resource(res_ops.HOST, conditions, None)
    if len(candidate_hosts) == 0:
        test_util.test_fail('Not find available Hosts to do migration')

    vm.migrate(candidate_hosts[0].uuid)

def create_volume(volume_creation_option=None, session_uuid = None, from_offering=True):
    if not volume_creation_option:
        disk_offering = test_lib.lib_get_disk_offering_by_name(os.getenv('smallDiskOfferingName'))
        volume_creation_option = test_util.VolumeOption()
        volume_creation_option.set_disk_offering_uuid(disk_offering.uuid)
        volume_creation_option.set_name('vr_test_volume')

    volume_creation_option.set_session_uuid(session_uuid)
    volume = zstack_volume_header.ZstackTestVolume()
    volume.set_creation_option(volume_creation_option)
    volume.create(from_offering)
    return volume

def migrate_vm_to_random_host(vm):
    test_util.test_dsc("migrate vm to random host")
    if not test_lib.lib_check_vm_live_migration_cap(vm.vm):
        test_util.test_skip('skip migrate if live migrate not supported')
    target_host = test_lib.lib_find_random_host(vm.vm)
    current_host = test_lib.lib_find_host_by_vm(vm.vm)
    vm.migrate(target_host.uuid)

    new_host = test_lib.lib_get_vm_host(vm.vm)
    if not new_host:
        test_util.test_fail('Not find available Hosts to do migration')

    if new_host.uuid != target_host.uuid:
        test_util.test_fail('[vm:] did not migrate from [host:] %s to target [host:] %s, but to [host:] %s' % (vm.vm.uuid, current_host.uuid, target_host.uuid, new_host.uuid))
    else:
        test_util.test_logger('[vm:] %s has been migrated from [host:] %s to [host:] %s' % (vm.vm.uuid, current_host.uuid, target_host.uuid))


class DataMigration(TestChain):
    def __init__(self, chain_head=None, chain_length=20):
        self.vm = None
        self.data_volume = None
        self.dst_ps = None
        self.image_name = os.getenv('imageName_windows')
        self.image_name_net = os.getenv('imageName_net')
        self.ceph_ps_name = os.getenv('cephPrimaryStorageName')
        self.ceph_ps_name_2 = os.getenv('cephPrimaryStorageName2')
        self.ceph_bs_name = os.getenv('cephBackupStorageName')
        self.ceph_bs_name_2 = os.getenv('cephBackupStorageName2')
        self.vol_job_name = "APIPrimaryStorageMigrateVolumeMsg"
        self.image_job_name = "APIBackupStorageMigrateImageMsg"
        self.origin_ps = None
        self.former_root_vol_install_path = None
        self.former_root_vol_size = None
        self.image = None
        self.test_chain = None
        self.cloned_vms = None
        self.test_obj_dict = None
        self.snapshots = None
        self.vol_uuid = None
        self.snapshot = []
        self.sp_tree = test_util.SPTREE()
        self.sp_type =None
        super(DataMigration, self).__init__(chain_head, chain_length)

    def get_current_ps(self):
        _ps1 = [os.getenv('cephPrimaryStorageName'), os.getenv('nfsPrimaryStorageName')]
        _ps2 = [os.getenv('cephPrimaryStorageName2'), os.getenv('nfsPrimaryStorageName2')]
        self.ps_1_name = [pn for pn in _ps1 if pn][0]
        self.ps_2_name = [pn2 for pn2 in _ps2 if pn2][0]

    def get_image(self, image_name=None):
        if not image_name:
            image_name = self.image_name_net
        if not self.image:
            conditions = res_ops.gen_query_conditions('name', '=', image_name)
            self.image = res_ops.query_resource(res_ops.IMAGE, conditions)[0]
        self.origin_bs = self.get_bs_inv(self.image.backupStorageRefs[0].backupStorageUuid)
        self.image_origin_path = self.image.backupStorageRefs[0].installPath

    def get_ps(self):
        self.get_current_ps()
        cond = res_ops.gen_query_conditions('name', '=', self.ps_1_name)
        self.ps_1 = res_ops.query_resource(res_ops.PRIMARY_STORAGE, cond)[0]
        cond2 = res_ops.gen_query_conditions('name', '=', self.ps_2_name)
        self.ps_2 = res_ops.query_resource(res_ops.PRIMARY_STORAGE, cond2)[0]

    def get_ps_inv(self, uuid):
        cond = res_ops.gen_query_conditions('uuid', '=', uuid)
        ps_inv = res_ops.query_resource(res_ops.PRIMARY_STORAGE, cond)[0]
        return ps_inv

    def get_bs_inv(self, uuid):
        cond = res_ops.gen_query_conditions('uuid', '=', uuid)
        bs_inv = res_ops.query_resource(res_ops.BACKUP_STORAGE, cond)[0]
        return bs_inv

    def get_bs(self):
        if self.ceph_bs_name:
            conditions = res_ops.gen_query_conditions('name', '=', self.ceph_bs_name)
            self.ceph_bs = res_ops.query_resource(res_ops.BACKUP_STORAGE, conditions)[0]
        if self.ceph_bs_name_2:
            conditions = res_ops.gen_query_conditions('name', '=', self.ceph_bs_name_2)
            self.ceph_bs_2 = res_ops.query_resource(res_ops.BACKUP_STORAGE, conditions)[0]

    def create_vm(self, image_name=None):
        '''
        {"next": ["create_snapshot", "create_image", "migrate_vm", "clone_vm", "migrate_image"],
         "skip": ["migrate_data_volume", "create_data_volume(from_offering=False)"]}
        '''
#         if self.vm:
#             self.vm.destroy()
        if self.cloned_vms:
            try:
                for vm in self.cloned_vms:
                    vm.stop()
#                     vm.destroy()
            except:
                pass
        self.get_image()
        self.vm = create_vm('multicluster_basic_vm', self.image.name, os.getenv('l3PublicNetworkName'))
        self.root_vol_uuid = self.vm.vm.rootVolumeUuid
        self.vm.check()
        self.origin_ps = self.get_ps_inv(self.vm.vm.allVolumes[0].primaryStorageUuid)
        return self

    def clone_vm(self):
        '''
        {"next": ["create_image", "migrate_vm", "create_snapshot"]}
        '''
        self.root_vol_uuid_list = []
        self.cloned_vms = self.vm.clone(['cloned-vm1', 'cloned-vm2'])
        for vm in self.cloned_vms:
            self.root_vol_uuid_list.append(vm.vm.rootVolumeUuid)
        self.vm = self.cloned_vms[-1]
        return self

    def migrate_vm(self, cloned=False, vms=[], start=True):
        '''
        {"must": 
                {"before": ["copy_data"],
                 "after": ["check_data", "check_origin_data_exist", "clean_up_ps_trash_and_check"]},
         "next": ["create_snapshot", "create_image", "migrate_vm", "clone_vm"],
         "weight": 2}
        '''
#         self.dst_ps = self.get_ps_candidate()
        self.former_root_vol_uuid = self.vm.vm.rootVolumeUuid
        self.former_root_vol_size = self.vm.vm.allVolumes[0].size
        self.former_root_vol_install_path = self.vm.vm.allVolumes[0].installPath
        self.origin_ps = self.get_ps_inv(self.vm.vm.allVolumes[0].primaryStorageUuid)
        if not vms:
            if not cloned:
                self.vm.stop()
                self.vm.detach_volume()
                ps_uuid_to_migrate = self.get_ps_candidate().uuid
                datamigr_ops.ps_migrage_root_volume(ps_uuid_to_migrate, self.vm.vm.rootVolumeUuid)
                conditions = res_ops.gen_query_conditions('uuid', '=', self.vm.vm.uuid)
                self.vm.vm = res_ops.query_resource(res_ops.VM_INSTANCE, conditions)[0]
                if start:
                    self.vm.start()
                    self.vm.check()
                    assert self.vm.vm.allVolumes[0].primaryStorageUuid == ps_uuid_to_migrate
                    self.root_vol_uuid = self.vm.vm.rootVolumeUuid
            else:
                for i in range(len(self.cloned_vms)):
                    self.cloned_vms[i].stop()
                    ps_uuid_to_migrate = self.get_ps_candidate(self.root_vol_uuid_list[i]).uuid
                    datamigr_ops.ps_migrage_root_volume(ps_uuid_to_migrate, self.root_vol_uuid_list[i])
                    conditions = res_ops.gen_query_conditions('uuid', '=', self.cloned_vms[i].vm.uuid)
                    self.cloned_vms[i].vm = res_ops.query_resource(res_ops.VM_INSTANCE, conditions)[0]
                    if start:
                        self.cloned_vms[i].start()
                        self.cloned_vms[i].check()
                        assert self.cloned_vms[i].vm.allVolumes[0].primaryStorageUuid == ps_uuid_to_migrate
        else:
            vms2 = []
            for vm in vms:
                vm.stop()
                ps_uuid_to_migrate = self.get_ps_candidate().uuid
                root_vol_uuid = vm.get_vm().rootVolumeUuid
                self.get_ps_candidate(root_vol_uuid)
                datamigr_ops.ps_migrage_root_volume(ps_uuid_to_migrate, root_vol_uuid)
                conditions = res_ops.gen_query_conditions('uuid', '=', vm.vm.uuid)
                vm.vm = res_ops.query_resource(res_ops.VM_INSTANCE, conditions)[0]
                if start:
                    vm.start()
                    vm.check()
                vms2.append(vm)
            return vms2
        return self
    
    def resize_vm(self, new_size):
        self.root_vol_uuid = self.vm.vm.rootVolumeUuid
        vol_ops.resize_volume(self.root_vol_uuid, new_size)
        conditions = res_ops.gen_query_conditions('uuid', '=', self.vm.vm.uuid)
        self.vm.vm = res_ops.query_resource(res_ops.VM_INSTANCE, conditions)[0]
        return self

    def resize_data_volume(self,new_size):
        self.data_vol_uuid = self.data_volume.get_volume().uuid
        vol_ops.resize_data_volume(self.data_vol_uuid, new_size)
	conditions = res_ops.gen_query_conditions('uuid', '=', self.data_vol_uuid)
	self.data_volume.data_volume = res_ops.query_resource(res_ops.VOLUME, conditions)[0]
        return self

    def migrate_data_volume(self):
        '''
        {"must": 
                {"before": ["mount_disk_in_vm", "copy_data", "detach_vm", "migrate_vm"],
                 "after": ["attach_vm", "mount_disk_in_vm", "check_data",
                           "check_origin_data_exist", "clean_up_ps_trash_and_check"]},
         "next": ["create_image", "create_snapshot"],
         "weight": 2}
         '''
        self.former_data_volume_uuid = self.data_volume.get_volume().uuid
        self.former_data_volume_size = self.data_volume.get_volume().size
        self.former_data_vol_installPath = self.data_volume.get_volume().installPath
#         if not self.dst_ps:
        self.dst_ps = self.get_ps_candidate(self.data_volume.get_volume().uuid)
        vol_migr_inv = datamigr_ops.ps_migrage_data_volume(self.dst_ps.uuid, self.data_volume.get_volume().uuid)
        cond_vol = res_ops.gen_query_conditions('uuid', '=', self.data_volume.get_volume().uuid)
        assert res_ops.query_resource(res_ops.VOLUME, cond_vol)
        self.data_volume_obsoleted = res_ops.query_resource(res_ops.VOLUME, cond_vol)[0]
        conditions = res_ops.gen_query_conditions('uuid', '=', vol_migr_inv.uuid)
        self.data_volume.set_volume(res_ops.query_resource(res_ops.VOLUME, conditions)[0])
        assert self.data_volume.get_volume().primaryStorageUuid == self.dst_ps.uuid
        self.set_ceph_mon_env(self.dst_ps.uuid)
        return self

    def create_snapshot(self):
        '''
        {"next": ["create_image", "migrate_vm", "clone_vm", "migrate_data_volume"],
         "delay": ["delete_snapshot"],
         "weight": 2}
        '''
        if not self.test_obj_dict:
            self.test_obj_dict = test_state.TestStateDict()
        self.test_obj_dict.add_vm(self.vm)
        if not self.data_volume:
            vol_uuid = self.vm.vm.rootVolumeUuid
        else:
            self.test_obj_dict.add_volume(self.data_volume)
            vol_uuid = self.data_volume.get_volume().uuid
        self.snapshots = self.test_obj_dict.get_volume_snapshot(vol_uuid) if self.vol_uuid != vol_uuid else self.snapshots
        self.vol_uuid = vol_uuid
        self.snapshots.set_utility_vm(self.vm)
        self.snapshots.create_snapshot('snapshot-%s' % time.strftime('%m%d-%H%M%S', time.localtime()))
#         self.snapshots.check()
        curr_sp = self.snapshots.get_current_snapshot()
        self.snapshot.append(curr_sp)
        if curr_sp.get_snapshot().type == 'Storage':
            self.sp_type = curr_sp.get_snapshot().type
            if not self.sp_tree.root:
                self.sp_tree.add('root')
            self.sp_tree.revert(self.sp_tree.root)
        self.sp_tree.add(curr_sp.get_snapshot().uuid)
        self.sp_tree.show_tree()
        return self

    def delete_snapshot(self):
        '''
        {"next": ["create_image", "migrate_vm", "clone_vm", "migrate_data_volume"]}
        '''
        snapshot = random.choice(self.snapshot)
        self.snapshots.delete_snapshot(snapshot)
        self.snapshot.remove(snapshot)
        return self

    def del_obsoleted_data_volume(self):
        vol_ops.delete_volume(self.data_volume_obsoleted.uuid)

    def copy_data(self):
        cmd = "find /home -iname 'zstack-woodpecker.*'"
        file_path = commands.getoutput(cmd).split('\n')[0]
        src_file_md5 = commands.getoutput('md5sum %s' % file_path).split(' ')[0]
        vm_ip = self.vm.get_vm().vmNics[0].ip
        cp_cmd = 'sshpass -p password scp -o StrictHostKeyChecking=no %s root@%s:/mnt/' % (file_path, vm_ip)
        sync_cmd = 'sshpass -p password ssh -o LogLevel=quiet -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no \
                   root@%s "sync;sync;sleep 60;sync"' % vm_ip
        for cmd in [cp_cmd, sync_cmd]:
            os.system(cmd)
        md5_cmd = 'sshpass -p password ssh -o LogLevel=quiet -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no \
                   root@%s md5sum /mnt/%s' % (vm_ip, file_path.split('/')[-1])
        dst_file_md5 = commands.getoutput(md5_cmd).split(' ')[0]
        test_util.test_dsc('src_file_md5: [%s], dst_file_md5: [%s]' % (src_file_md5, dst_file_md5))
        assert dst_file_md5 == src_file_md5, 'dst_file_md5 [%s] and src_file_md5 [%s] is not match, stop test' % (src_file_md5, dst_file_md5)
        return self

    def check_data(self):
        check_cmd = '''sshpass -p password ssh -o LogLevel=quiet -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no root@%s \
        "tar xvf /mnt/zstack-woodpecker.tar -C /mnt > /dev/null &>1; grep scenario_config_path /mnt/zstackwoodpecker/zstackwoodpecker/test_lib.py && echo 0 || echo 1" \
        ''' % (self.vm.get_vm().vmNics[0].ip)
        ret = commands.getoutput(check_cmd).split('\n')[-1]
        assert ret == '0', "data check failed!, the return code is %s, 0 is expected" % ret
        return self

    def check_origin_data_exist(self, root_vol=True):
        if root_vol:
            vol_installPath = self.former_root_vol_install_path
            vol_uuid = self.former_root_vol_uuid
            vol_size = self.former_root_vol_size
        else:
            vol_installPath = self.former_data_vol_installPath
            vol_uuid = self.former_data_volume_uuid
            vol_size = self.former_data_volume_size
        if self.origin_ps.type == 'Ceph':
            ceph_mon_ip = self.origin_ps.mons[0].monAddr
            self.chk_cmd = 'sshpass -p password ssh -o LogLevel=quiet -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no root@%s "rbd info %s --format=json"' \
                        % (ceph_mon_ip, vol_installPath.split('ceph://')[-1])
            data_info = shell.call(self.chk_cmd)
            origin_meta = jsonobject.loads(data_info)
#             assert origin_meta.name == vol_uuid
            if root_vol:
                assert origin_meta.size == vol_size
            else:
                assert origin_meta.size >= vol_size
            assert 'rbd_data' in origin_meta.block_name_prefix
            ps_trash = ps_ops.get_trash_on_primary_storage(self.origin_ps.uuid).storageTrashSpecs
            trash_install_path_list = [trsh.installPath for trsh in ps_trash]
            assert vol_installPath in trash_install_path_list
        else:
            nfs_ip, mount_path = self.origin_ps.url.split(':')
            self.chk_cmd = 'sshpass -p password ssh -o LogLevel=quiet -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no \
                            root@%s "qemu-img info %s"' % (nfs_ip, mount_path + vol_installPath.split(self.origin_ps.uuid)[-1])
            data_info = shell.call(self.chk_cmd)
            assert str(vol_size) in data_info
            ps_trash = ps_ops.get_trash_on_primary_storage(self.origin_ps.uuid).storageTrashSpecs
            trash_install_path_list = [trsh.installPath for trsh in ps_trash]
            assert '/'.join(vol_installPath.split('/')[:8]) in trash_install_path_list
        return self

    def check_vol_sp(self, vol_uuid, count):
        cond = res_ops.gen_query_conditions('volumeUuid', '=', vol_uuid)
        vol_sp_tree = res_ops.query_resource(res_ops.VOLUME_SNAPSHOT, cond)
        assert len(vol_sp_tree) == count

    def check_origin_image_exist(self):
        self.chk_cmd_img = 'sshpass -p password ssh -o LogLevel=quiet -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no root@%s "rbd info %s --format=json"' \
                        % (self.origin_bs.mons[0].monAddr, self.image_origin_path.split('ceph://')[-1])
        img_info = shell.call(self.chk_cmd_img)
        origin_meta = jsonobject.loads(img_info)
        test_util.test_dsc('origin image meta: %s' % origin_meta)
        assert origin_meta.name == self.image_origin_path.split('/')[-1]
        assert origin_meta.size == self.image.size
        assert 'rbd_data' in origin_meta.block_name_prefix
        return self

    def clean_up_single_image_trash(self):
        trashes = bs_ops.get_trash_on_backup_storage(self.origin_bs.uuid)
        for t in trashes:
            if self.image.uuid == t.resourceUuid:
                trash_id = t.trashId
                break
        bs_ops.clean_up_trash_on_backup_storage(self.origin_bs.uuid, trash_id)
        trashes = bs_ops.get_trash_on_backup_storage(self.origin_bs.uuid)
        if trashes:
            for t in trashes:
                if self.image.uuid in t.installPath:
                    test_util.test_fail('image trash cleanup failed!')

    def clean_up_single_volume_trash(self):
        trashes = ps_ops.get_trash_on_primary_storage(self.origin_ps.uuid).storageTrashSpecs
        for t in trashes:
            if self.vm.vm.rootVolumeUuid == t.resourceUuid:
                trash_id = t.trashId
                break
        ps_ops.clean_up_trash_on_primary_storage(self.origin_ps.uuid, trash_id)
        trashes = ps_ops.get_trash_on_primary_storage(self.origin_ps.uuid).storageTrashSpecs
        if trashes:
            for t in trashes:
                if self.image.uuid in t.installPath:
                    test_util.test_fail('image trash cleanup failed!')

    def clean_up_bs_trash_and_check(self):
        bs_ops.clean_up_trash_on_backup_storage(self.origin_bs.uuid)
        assert not bs_ops.get_trash_on_backup_storage(self.origin_bs.uuid)
        try:
            shell.call(self.chk_cmd_img)
        except Exception as e:
            if 'No such file or directory' in str(e):
                pass
            else:
                raise e
        return self

    def clean_up_ps_trash_and_check(self, target_ps_uuid=None):
        target_ps_uuid = target_ps_uuid if target_ps_uuid else self.origin_ps.uuid
        ps_ops.clean_up_trash_on_primary_storage(target_ps_uuid)
        if not target_ps_uuid:
            assert not ps_ops.get_trash_on_primary_storage(self.origin_ps.uuid).storageTrashSpecs
            try:
                shell.call(self.chk_cmd)
            except Exception as e:
                if 'No such file or directory' in str(e):
                    pass
                else:
                    raise e
        return self

    def migrate_image(self, image_name=None):
        '''
        {"must": 
                {"after": ["check_origin_image_exist", "clean_up_bs_trash_and_check"]},
         "next": ["create_vm", "create_snapshot", "create_data_volume(from_offering=False)"],
         "weight": 1}
        '''
        self.get_image(image_name)
        dst_bs = self.get_bs_candidate()
        image_migr_inv = datamigr_ops.bs_migrage_image(dst_bs.uuid, self.image.backupStorageRefs[0].backupStorageUuid, self.image.uuid)
        conditions = res_ops.gen_query_conditions('uuid', '=', self.image.uuid)
        assert res_ops.query_resource(res_ops.IMAGE, conditions)
        conditions = res_ops.gen_query_conditions('uuid', '=', image_migr_inv.uuid)
        self.image = res_ops.query_resource(res_ops.IMAGE, conditions)[0]
        assert self.image.backupStorageRefs[0].backupStorageUuid == dst_bs.uuid
        return self

    def get_bs_for_image_creation(self):
        vm_ps_uuid = self.vm.vm.allVolumes[0].primaryStorageUuid
        ps_cond = res_ops.gen_query_conditions('uuid', '=', vm_ps_uuid)
        ps_fsid = res_ops.query_resource(res_ops.PRIMARY_STORAGE, ps_cond)[0].fsid
        all_bs = res_ops.query_resource(res_ops.BACKUP_STORAGE)
        return [bs for bs in all_bs if bs.fsid == ps_fsid][0]

    def get_ps_for_volume_creation(self):
        image_bs_uuid = self.image.backupStorageRefs[0].backupStorageUuid
        bs_cond = res_ops.gen_query_conditions('uuid', '=', image_bs_uuid)
        bs_fsid = res_ops.query_resource(res_ops.BACKUP_STORAGE, bs_cond)[0].fsid
        all_ps = res_ops.query_resource(res_ops.PRIMARY_STORAGE)
        return [ps for ps in all_ps if ps.fsid == bs_fsid][0]

    def create_image(self):
        '''
        {"next": ["migrate_image", "create_vm", "create_snapshot", "create_data_volume(from_offering=False)"]}
        '''
        _bs = self.query_bs()
        if _bs.type == 'Ceph':
            bs = self.get_bs_for_image_creation()
        else:
            bs = _bs
        image_creation_option = test_util.ImageOption()
        image_creation_option.set_backup_storage_uuid_list([bs.uuid])
        if not self.data_volume:
            self._image_name = 'root-volume-created-image-%s' % time.strftime('%y%m%d-%H%M%S', time.localtime())
            image_creation_option.set_root_volume_uuid(self.vm.vm.rootVolumeUuid)
            root = True
        else:
            self._image_name = 'data-volume-created-image-%s' % time.strftime('%y%m%d-%H%M%S', time.localtime())
            image_creation_option.set_data_volume_uuid(self.data_volume.get_volume().uuid)
            root = False
        image_creation_option.set_name(self._image_name)
        self._image = test_image.ZstackTestImage()
        self._image.set_creation_option(image_creation_option)
        self._image.create(root=root)
        self.image = self._image.image
        if bs.type.lower() == 'ceph':
            bs_mon_ip = bs.mons[0].monAddr
            os.environ['cephBackupStorageMonUrls'] = 'root:password@%s' % bs_mon_ip
#         self._image.check()
        return self

    def get_ps_candidate(self, vol_uuid=None):
        if not vol_uuid:
            vol_uuid = self.vm.vm.rootVolumeUuid
        ps_to_migrate = random.choice(datamigr_ops.get_ps_candidate_for_vol_migration(vol_uuid))
#         assert len(self.cand_ps) == 1
#         self.get_ps()
#         ps_to_migrate = self.ps_1 if self.ps_1.uuid != self.vm.vm.allVolumes[0].primaryStorageUuid else self.ps_2
        return ps_to_migrate

    def get_bs_candidate(self):
        self.get_image()
        self.cand_bs = datamigr_ops.get_bs_candidate_for_image_migration(self.image.backupStorageRefs[0].backupStorageUuid)
        assert len(self.cand_bs) == 1
        self.get_bs()
        bs_to_migrate = self.ceph_bs if self.ceph_bs.uuid != self.image.backupStorageRefs[0].backupStorageUuid else self.ceph_bs_2
        return bs_to_migrate

    def query_bs(self):
        bs = res_ops.query_resource(res_ops.BACKUP_STORAGE)[0]
        return bs

    def check_ps_candidate(self):
        ps_to_migrate = self.get_ps_candidate()
        assert ps_to_migrate.uuid != self.vm.vm.allVolumes[0].primaryStorageUuid

    def check_bs_candidate(self):
        bs_type = self.query_bs().type
        if bs_type == 'Ceph':
            bs_to_migrate = self.get_bs_candidate()
            assert self.cand_bs[0].uuid == bs_to_migrate.uuid

    def create_data_volume(self, sharable=False, vms=[], from_offering=True):
        '''
        {"next": ["migrate_data_volume", "create_image", "create_snapshot"],
         "skip": ["create_vm", "clone_vm", "migrate_vm"]}
        '''
        conditions = res_ops.gen_query_conditions('name', '=', os.getenv('largeDiskOfferingName'))
        disk_offering_uuid = res_ops.query_resource(res_ops.DISK_OFFERING, conditions)[0].uuid
        volume_option = test_util.VolumeOption()
        if from_offering:
            volume_option.set_disk_offering_uuid(disk_offering_uuid)
            ps_uuid = self.vm.vm.allVolumes[0].primaryStorageUuid
        else:
            volume_option.set_volume_template_uuid(self.image.uuid)
            ps_uuid = self.get_ps_for_volume_creation().uuid
        volume_option.set_name('data_volume_for_migration')
        volume_option.set_primary_storage_uuid(ps_uuid)
        if sharable:
            volume_option.set_system_tags(['ephemeral::shareable', 'capability::virtio-scsi'])
        self.data_volume = create_volume(volume_option, from_offering=from_offering)
        self.set_ceph_mon_env(ps_uuid)
        if vms:
            for vm in vms:
                self.data_volume.attach(vm)
        else:
            if ps_uuid != self.vm.vm.allVolumes[0].primaryStorageUuid:
                self.migrate_vm()
                self.clean_up_ps_trash_and_check(ps_uuid)
            self.data_volume.attach(self.vm)
        self.data_volume.check()
        if from_offering:
            test_lib.lib_mkfs_for_volume(self.data_volume.get_volume().uuid, self.vm.vm, '/mnt')
        return self

    def revert_sp(self, sp=None, start_vm=False):
        '''
        {"must":{"before": ["create_sp"]},
        "next": ["create_sp", "batch_del_sp"],
        "weight": 2}
        '''
        if self.data_volume:
            try:
                self.data_volume.detach()
            except:
                pass
        else:
            self.vm.stop()
        if not sp:
            sp = random.choice(self.snapshot)
        self.snapshots.use_snapshot(sp)
        if start_vm:
            self.vm.start()
            self.vm.check()
        if self.sp_type != 'Storage':
            self.sp_tree.revert(sp.get_snapshot().uuid)
        if self.data_volume:
            try:
                self.data_volume.attach(self.vm)
            except:
                pass
        self.sp_tree.show_tree()
        return self

    def sp_check(self):
        self.snapshots.check()
        return self

    def batch_del_sp(self, snapshot_uuid_list=None, exclude_root=True):
        '''
        {"must":{"before": ["create_sp"]},
        "next": ["create_sp", "revert_sp(start_vm=True)"],
        "weight": 1}
        '''
        for _ in range(5):
            random.shuffle(self.snapshot)
        if not snapshot_uuid_list:
            snapshot_list = self.snapshot[:random.randint(2, len(self.snapshot))]
            snapshot_uuid_list = [spt.get_snapshot().uuid for spt in snapshot_list]
        spd = {_sp.get_snapshot().uuid: _sp for _sp in self.snapshot}
        if exclude_root:
            if self.sp_tree.root in snapshot_uuid_list:
                snapshot_uuid_list.remove(self.sp_tree.root)
        vol_ops.batch_delete_snapshot(snapshot_uuid_list)
        for spuuid in snapshot_uuid_list:
            assert not res_ops.query_resource(res_ops.VOLUME_SNAPSHOT, res_ops.gen_query_conditions('uuid', '=', spuuid)), \
            'The snapshot with uuid [%s] is still exist!' % spuuid
            if self.sp_tree.delete(spuuid):
                self.snapshots.delete_snapshot(spd[spuuid], False)
        print self.sp_tree.tree
        remained_sp =  self.sp_tree.tree.keys()
        if self.sp_type == 'Storage':
            remained_sp.remove(self.sp_tree.root)
        for sud in spd.keys():
            if sud not in remained_sp:
                self.snapshot.remove(spd[sud])
        for sp_uuid in remained_sp:
            snapshot = res_ops.query_resource(res_ops.VOLUME_SNAPSHOT, res_ops.gen_query_conditions('uuid', '=', sp_uuid))
            assert snapshot, 'The snapshot with uuid [%s] was not found!' % sp_uuid
            if snapshot[0].parentUuid:
                assert snapshot[0].parentUuid == self.sp_tree.parent(sp_uuid)
        remained_sp_num = len(self.sp_tree.get_all_nodes())
        if self.sp_type == 'Storage':
            remained_sp_num -= 1
        if not self.data_volume:
            actual_sp_num = len(res_ops.query_resource(res_ops.VOLUME_SNAPSHOT, res_ops.gen_query_conditions('volumeUuid', '=', self.vm.get_vm().allVolumes[0].uuid)))
        else:
            actual_sp_num = len(res_ops.query_resource(res_ops.VOLUME_SNAPSHOT, res_ops.gen_query_conditions('volumeUuid', '=', self.data_volume.get_volume().uuid)))
        assert actual_sp_num == remained_sp_num, 'actual remained snapshots number: %s, snapshot number in sp tree: %s' % (actual_sp_num, remained_sp_num)
        self.sp_tree.show_tree()
        self.snapshots.check()
        return self

    def attach_vm(self):
        self.data_volume.attach(self.vm)
        return self

    def detach_vm(self):
        self.data_volume.detach()
        return self

    def mount_disk_in_vm(self):
        import tempfile
        script_file = tempfile.NamedTemporaryFile(delete=False)
        script_file.write('''device="/dev/`ls -ltr --file-type /dev | awk '$4~/disk/ {print $NF}' | grep -v '[[:digit:]]'| sort | tail -1`" \n mount ${device}1 /mnt''')
        script_file.close()
        test_lib.lib_execute_shell_script_in_vm(self.vm.vm, script_file.name)
        return self

    def set_ceph_mon_env(self, ps_uuid):
        cond_vol = res_ops.gen_query_conditions('uuid', '=', ps_uuid)
        ps = res_ops.query_resource(res_ops.PRIMARY_STORAGE, cond_vol)[0]
        if ps.type.lower() == 'ceph':
            ps_mon_ip = ps.mons[0].monAddr
            os.environ['cephBackupStorageMonUrls'] = 'root:password@%s' % ps_mon_ip

    def submit_longjob(self, job_data, name, job_type=None):
        if job_type == 'image':
            _job_name = self.image_job_name
        else:
            _job_name = self.vol_job_name
        long_job = longjob_ops.submit_longjob(_job_name, job_data, name)
        assert long_job.state == "Running"
        cond_longjob = res_ops.gen_query_conditions('apiId', '=', long_job.apiId)
        for _ in xrange(60):
            longjob = res_ops.query_resource(res_ops.LONGJOB, cond_longjob)[0]
            if longjob.state == "Succeeded":
                break
            else:
                time.sleep(5)
        assert longjob.state == "Succeeded"
        assert longjob.jobResult == "Succeeded"

    def longjob_migr_vm(self):
        self.vm.stop()
        name = "long_job_of_%s" % self.vm.vm.name
        self.dst_ps = self.get_ps_candidate()
        job_data = '{"volumeUuid": %s, "dstPrimaryStorageUuid": %s}' % (self.vm.vm.rootVolumeUuid, self.dst_ps.uuid)
        self.submit_longjob(job_data, name)
        self.vm.start()
        self.vm.check()
        assert self.vm.vm.allVolumes[0].primaryStorageUuid == self.dst_ps.uuid

    def longjob_migr_data_vol(self):
        vol_uuid = self.data_volume.get_volume().uuid
        name = "long_job_of_%s" % self.data_volume.get_volume().name
        if not self.dst_ps:
            self.dst_ps = self.get_ps_candidate(vol_uuid)
        job_data = '{"volumeUuid": %s, "dstPrimaryStorageUuid": %s}' % (vol_uuid, self.dst_ps.uuid)
        self.submit_longjob(job_data, name)
        cond_vol = res_ops.gen_query_conditions('uuid', '=', vol_uuid)
        self.data_volume.set_volume(res_ops.query_resource(res_ops.VOLUME, cond_vol)[0])
        assert self.data_volume.get_volume().primaryStorageUuid == self.dst_ps.uuid

    def longjob_migr_image(self):
        self.dst_bs = self.get_bs_candidate()
        self.get_image(os.getenv('imageName_windows'))
        name = "long_job_of_%s" % self.image.name
        job_data = '{"imageUuid": %s, "srcBackupStorageUuid": %s, "dstBackupStorageUuid": %s}' % (self.image.uuid, self.image.backupStorageRefs[0].backupStorageUuid, self.dst_bs.uuid)
        self.submit_longjob(job_data, name, job_type='image')
        cond_image = res_ops.gen_query_conditions('uuid', '=', self.image.uuid)
        self.image = res_ops.query_resource(res_ops.IMAGE, cond_image)[0]
        assert self.image.backupStorageRefs[0].backupStorageUuid == self.dst_bs.uuid


def get_host_cpu_model(ip):
    cmd = 'virsh capabilities | grep "<arch>.*.</arch>" -C 1 | tail -1'
    result = test_lib.lib_execute_ssh_cmd(ip, 'root', 'password',cmd)
    return result[13:-9]


def set_host_cpu_model(ip,model=None):
    i = 0
    _model = get_host_cpu_model(ip)
    test_util.test_logger(_model)
    while _model != model:
        i += 1
        if i > 5:
            test_util.test_fail("set host cpu model faild")
        cmd = '''sed -i "s/'{}'/'{}'/g" /usr/share/libvirt/cpu_map.xml'''.format(_model,model)
        test_lib.lib_execute_ssh_cmd(ip, 'root', 'password',cmd)
        cmd = "systemctl restart libvirtd"
        test_lib.lib_execute_ssh_cmd(ip, 'root', 'password',cmd)
        _model = get_host_cpu_model(ip)


class AliyunNAS(hybrid_test_stub.HybridObject):
    def __init__(self):
        self.nas_fs_name = 'test-nas-file-system'
        self.acc_grp = None
        self.acc_grp_rule = None
        self.nas_fs = None
        self.nas_mnt_target = None

    def get_dc(self):
        self.dc = hyb_ops.query_datacenter_local()[0]

    def create_nas_fs(self, storage_type='Capacity', protocol='NFS'):
        self.get_dc()
        name = 'aliyun-nas-fs-' + str(time.time())[:-3]
        self.nas_fs = nas_ops.create_aliyun_nas_file_system(self.dc.uuid, name=name, storage_type=storage_type, protocol=protocol)
        self.check_resource('create', 'name', name, 'query_nas_file_system', aliyun_nas=True)

    def del_nas_fs(self):
        nas_ops.delete_nas_file_system(self.nas_fs.uuid)
        self.check_resource('delete', 'fileSystemId', self.nas_fs.fileSystemId, 'query_nas_file_system', aliyun_nas=True)

    def crt_nas_mount_target(self):
        self.create_nas_fs()

    def crt_access_grp(self, network_type='classic'):
        self.get_dc()
        self.grp_name = 'aliyun-nas-acc-grp-' + str(time.time())[:-3]
        self.acc_grp = nas_ops.create_aliyun_nas_access_group(self.dc.uuid, self.grp_name, network_type=network_type)
        self.check_resource('create', 'name', self.grp_name, 'query_aliyun_nas_access_group', aliyun_nas=True)

    def del_acc_grp(self):
        nas_ops.delete_aliyun_nas_access_group(self.acc_grp.uuid)
        self.check_resource('delete', 'name', self.grp_name, 'query_nas_file_system', aliyun_nas=True)

    def crt_acc_grp_rule(self, source_cidr='172.26.0.0/24', rw_type='RDWR'):
        self.crt_access_grp()
        self.grp_rule = nas_ops.create_aliyun_nas_access_group_rule(self.acc_grp.uuid, source_cidr=source_cidr, rw_type=rw_type)
        cond_acc_grp = res_ops.gen_query_conditions('name', '=', self.grp_name)
        self.acc_grp = nas_ops.query_aliyun_nas_access_group(cond_acc_grp)[0]
        assert self.acc_grp.rules[0].sourceCidr == source_cidr

    def del_acc_grp_rule(self):
        nas_ops.delete_aliyun_nas_access_group_rule(self.grp_rule.uuid)
        cond_acc_grp = res_ops.gen_query_conditions('name', '=', self.grp_name)
        self.acc_grp = nas_ops.query_aliyun_nas_access_group(cond_acc_grp)[0]
        assert not self.acc_grp.rules

    def get_aliyun_nas_fs(self):
        self.get_dc()
        fs_remote = nas_ops.get_aliyun_nas_file_system_remote(self.dc.uuid)[0]
        assert fs_remote.fileSystemId == os.getenv('fileSystemId')

    def get_aliyun_nas_acc_grp(self):
        self.get_dc()
        grp_remote = nas_ops.get_aliyun_nas_access_group_remote(self.dc.uuid)[0]
        assert grp_remote.name == os.getenv('groupName')

    def get_aliyun_nas_mount_target(self):
        cond_fs = res_ops.gen_query_conditions('fileSystemId', '=', os.getenv('fileSystemId'))
        nas_fs = nas_ops.query_nas_file_system(cond_fs)[0]
        mtarget = nas_ops.get_aliyun_nas_mount_target_remote(nas_fs.uuid)[0]
        assert mtarget.mountDomain == os.getenv('mountDomain')

def execute_shell_in_process(cmd, tmp_file, timeout = 3600, no_timeout_excep = False):
    logfd = open(tmp_file, 'w', 0)
    process = subprocess.Popen(cmd, executable='/bin/sh', shell=True, stdout=logfd, stderr=logfd, universal_newlines=True)

    start_time = time.time()
    while process.poll() is None:
        curr_time = time.time()
        test_time = curr_time - start_time
        if test_time > timeout:
            process.kill()
            logfd.close()
            logfd = open(tmp_file, 'r')
            test_util.test_logger('[shell:] %s [timeout logs:] %s' % (cmd, '\n'.join(logfd.readlines())))
            logfd.close()
            if no_timeout_excep:
                test_util.test_logger('[shell:] %s timeout, after %d seconds' % (cmd, test_time))
                return 1
            else:
                os.system('rm -f %s' % tmp_file)
                test_util.test_fail('[shell:] %s timeout, after %d seconds' % (cmd, timeout))
        if test_time%10 == 0:
            print('shell script used: %ds' % int(test_time))
        time.sleep(1)
    logfd.close()
    logfd = open(tmp_file, 'r')
    test_util.test_logger('[shell:] %s [logs]: %s' % (cmd, '\n'.join(logfd.readlines())))
    logfd.close()
    return process.returncode
