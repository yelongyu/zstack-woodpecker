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
import zstackwoodpecker.header.host as host_header
import zstacklib.utils.jsonobject as jsonobject
from zstacklib.utils import shell
import threading
import time
import sys
import commands
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

def create_volume(volume_creation_option=None, session_uuid = None):
    if not volume_creation_option:
        disk_offering = test_lib.lib_get_disk_offering_by_name(os.getenv('smallDiskOfferingName'))
        volume_creation_option = test_util.VolumeOption()
        volume_creation_option.set_disk_offering_uuid(disk_offering.uuid)
        volume_creation_option.set_name('vr_test_volume')

    volume_creation_option.set_session_uuid(session_uuid)
    volume = zstack_volume_header.ZstackTestVolume()
    volume.set_creation_option(volume_creation_option)
    volume.create()
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


class DataMigration(object):
    def __init__(self):
        self.vm = None
        self.data_volume = None
        self.dst_ps = None
        self.image_name = os.getenv('imageName_s')
        self.image_name_net = os.getenv('imageName_net')
        self.ceph_ps_name = os.getenv('cephPrimaryStorageName')
        self.ceph_ps_name_2 = os.getenv('cephPrimaryStorageName2')
        self.ceph_bs_name = os.getenv('cephBackupStorageName')
        self.ceph_bs_name_2 = os.getenv('cephBackupStorageName2')
        self.vol_job_name = "APIPrimaryStorageMigrateVolumeMsg"
        self.image_job_name = "APIBackupStorageMigrateImageMsg"
        self.origin_ps = None
        self.root_vol_install_path = None
        self.root_vol_size = None

    def get_current_ps(self):
        _ps1 = [os.getenv('cephPrimaryStorageName'), os.getenv('nfsPrimaryStorageName')]
        _ps2 = [os.getenv('cephPrimaryStorageName2'), os.getenv('nfsPrimaryStorageName2')]
        self.ps_1_name = [pn for pn in _ps1 if pn][0]
        self.ps_2_name = [pn2 for pn2 in _ps2 if pn2][0]

    def get_image(self):
        conditions = res_ops.gen_query_conditions('name', '=', self.image_name_net)
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
        if not image_name:
            image_name = self.image_name_net
        self.vm = create_vm('multicluster_basic_vm', image_name, os.getenv('l3PublicNetworkName'))
        self.vm.check()
        self.root_vol_uuid = self.vm.vm.rootVolumeUuid
        self.root_vol_size = self.vm.vm.allVolumes[0].size
        self.root_vol_install_path = self.vm.vm.allVolumes[0].installPath
        self.origin_ps = self.get_ps_inv(self.vm.vm.allVolumes[0].primaryStorageUuid)
        return self.vm

    def clone_vm(self):
        self.root_vol_uuid_list = []
        self.cloned_vms = self.vm.clone(['cloned-vm1', 'cloned-vm2'])
        for vm in self.cloned_vms:
            self.root_vol_uuid_list.append(vm.vm.rootVolumeUuid)

    def migrate_vm(self, cloned=False, vms=[], start=True):
#         self.dst_ps = self.get_ps_candidate()
        if not vms:
            if not cloned:
                self.vm.stop()
                ps_uuid_to_migrate = self.get_ps_candidate().uuid
                datamigr_ops.ps_migrage_root_volume(ps_uuid_to_migrate, self.root_vol_uuid)
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

    def migrate_data_volume(self):
        if not self.dst_ps:
            self.dst_ps = self.get_ps_candidate(self.data_volume.get_volume().uuid)
        vol_migr_inv = datamigr_ops.ps_migrage_data_volume(self.dst_ps.uuid, self.data_volume.get_volume().uuid)
        cond_vol = res_ops.gen_query_conditions('uuid', '=', self.data_volume.get_volume().uuid)
        assert res_ops.query_resource(res_ops.VOLUME, cond_vol)
        self.data_volume_obsoleted = res_ops.query_resource(res_ops.VOLUME, cond_vol)[0]
        conditions = res_ops.gen_query_conditions('uuid', '=', vol_migr_inv.uuid)
        self.data_volume.set_volume(res_ops.query_resource(res_ops.VOLUME, conditions)[0])
        assert self.data_volume.get_volume().primaryStorageUuid == self.dst_ps.uuid
        self.set_ceph_mon_env(self.dst_ps.uuid)

    def del_obsoleted_data_volume(self):
        vol_ops.delete_volume(self.data_volume_obsoleted.uuid)

    def copy_data(self):
        cmd = "find /home -iname 'zstack-woodpecker.*'"
        file_path = commands.getoutput(cmd).split('\n')[0]
        cp_cmd = 'sshpass -p password scp -o StrictHostKeyChecking=no %s root@%s:/mnt/' % (file_path, self.vm.get_vm().vmNics[0].ip)
        commands.getoutput(cp_cmd)

    def check_data(self):
        check_cmd = '''sshpass -p password ssh -o LogLevel=quiet -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no root@%s \
        "tar xvf /mnt/zstack-woodpecker.tar -C /mnt > /dev/null &>1; grep scenario_config_path /mnt/zstackwoodpecker/zstackwoodpecker/test_lib.py && echo 0 || echo 1" \
        ''' % (self.vm.get_vm().vmNics[0].ip)
        ret = commands.getoutput(check_cmd).split('\n')[-1]
        assert ret == '0', "data check failed!, the return code is %s, 0 is expected" % ret

    def check_origin_data_exist(self, root_vol=True):
        if root_vol:
            vol_installPath = self.root_vol_install_path
            vol_uuid = self.root_vol_uuid
            vol_size = self.root_vol_size
        else:
            vol_installPath = self.data_vol_installPath
            vol_uuid = self.data_volume_uuid
            vol_size = self.data_volume_size
        if self.origin_ps.type == 'Ceph':
            ceph_mon_ip = self.origin_ps.mons[0].monAddr
            self.chk_cmd = 'sshpass -p password ssh -o LogLevel=quiet -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no root@%s "rbd info %s --format=json"' \
                        % (ceph_mon_ip, vol_installPath.split('ceph://')[-1])
            data_info = shell.call(self.chk_cmd)
            origin_meta = jsonobject.loads(data_info)
            assert origin_meta.name == vol_uuid
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
            assert vol_installPath[:-39] in trash_install_path_list

    def check_vol_sp(self, vol_uuid, count):
        cond = res_ops.gen_query_conditions('volumeUuid', '=', vol_uuid)
        vol_sp_tree = res_ops.query_resource(res_ops.VOLUME_SNAPSHOT, cond)
        assert len(vol_sp_tree) == count

    def check_origin_image_exist(self):
        self.chk_cmd_img = 'sshpass -p password ssh -o LogLevel=quiet -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no root@%s "rbd info %s --format=json"' \
                        % (self.origin_bs.mons[0].monAddr, self.image_origin_path.split('ceph://')[-1])
        img_info = shell.call(self.chk_cmd_img)
        origin_meta = jsonobject.loads(img_info)
        assert origin_meta.name == self.image.uuid
        assert origin_meta.size == self.image.size
        assert 'rbd_data' in origin_meta.block_name_prefix

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

    def clean_up_ps_trash_and_check(self):
        ps_ops.clean_up_trash_on_primary_storage(self.origin_ps.uuid)
        assert not ps_ops.get_trash_on_primary_storage(self.origin_ps.uuid).storageTrashSpecs
        try:
            shell.call(self.chk_cmd)
        except Exception as e:
            if 'No such file or directory' in str(e):
                pass
            else:
                raise e

    def migrate_image(self):
        self.get_image()
        dst_bs = self.get_bs_candidate()
        image_migr_inv = datamigr_ops.bs_migrage_image(dst_bs.uuid, self.image.backupStorageRefs[0].backupStorageUuid, self.image.uuid)
        conditions = res_ops.gen_query_conditions('uuid', '=', self.image.uuid)
        assert res_ops.query_resource(res_ops.IMAGE, conditions)
        conditions = res_ops.gen_query_conditions('uuid', '=', image_migr_inv.uuid)
        self.image = res_ops.query_resource(res_ops.IMAGE, conditions)[0]
        assert self.image.backupStorageRefs[0].backupStorageUuid == dst_bs.uuid

    def create_image(self):
        _bs = self.query_bs()
        if _bs.type == 'Ceph':
            bs = self.get_bs_candidate()
        else:
            bs = _bs
        self._image_name = 'vm-created-image-%s' % time.strftime('%y%m%d-%H%M%S', time.localtime())
        image_creation_option = test_util.ImageOption()
        image_creation_option.set_backup_storage_uuid_list([bs.uuid])
        image_creation_option.set_root_volume_uuid(self.vm.vm.rootVolumeUuid)
        image_creation_option.set_name(self._image_name)
        self._image = test_image.ZstackTestImage()
        self._image.set_creation_option(image_creation_option)
        self._image.create()
        if bs.type.lower() == 'ceph':
            bs_mon_ip = bs.mons[0].monAddr
            os.environ['cephBackupStorageMonUrls'] = 'root:password@%s' % bs_mon_ip
#         self._image.check()

    def get_ps_candidate(self, vol_uuid=None):
        if not vol_uuid:
            vol_uuid = self.root_vol_uuid
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

    def create_data_volume(self, sharable=False, vms=[]):
        conditions = res_ops.gen_query_conditions('name', '=', os.getenv('largeDiskOfferingName'))
        disk_offering_uuid = res_ops.query_resource(res_ops.DISK_OFFERING, conditions)[0].uuid
        ps_uuid = self.vm.vm.allVolumes[0].primaryStorageUuid
        volume_option = test_util.VolumeOption()
        volume_option.set_disk_offering_uuid(disk_offering_uuid)
        volume_option.set_name('data_volume_for_migration')
        volume_option.set_primary_storage_uuid(ps_uuid)
        if sharable:
            volume_option.set_system_tags(['ephemeral::shareable', 'capability::virtio-scsi'])
        self.data_volume = create_volume(volume_option)
        self.set_ceph_mon_env(ps_uuid)
        if vms:
            for vm in vms:
                self.data_volume.attach(vm)
        else:
            self.data_volume.attach(self.vm)
        self.data_volume.check()
        self.data_volume_uuid = self.data_volume.get_volume().uuid
        self.data_volume_size = self.data_volume.get_volume().size
        self.data_vol_installPath = self.data_volume.get_volume().installPath
        test_lib.lib_mkfs_for_volume(self.data_volume_uuid, self.vm.vm, '/mnt')

    def mount_disk_in_vm(self):
        import tempfile
        script_file = tempfile.NamedTemporaryFile(delete=False)
        script_file.write('''device="/dev/`ls -ltr --file-type /dev | awk '$4~/disk/ {print $NF}' | grep -v '[[:digit:]]' | tail -1`" \n mount ${device}1 /mnt''')
        script_file.close()
        test_lib.lib_execute_shell_script_in_vm(self.vm.vm, script_file.name)

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


