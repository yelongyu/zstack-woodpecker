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
import zstackwoodpecker.zstack_test.zstack_test_vm as test_vm_header
import zstackwoodpecker.header.host as host_header
import threading
import time
import sys
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

    def get_current_ps(self):
        _ps1 = [os.getenv('cephPrimaryStorageName'), os.getenv('nfsPrimaryStorageName')]
        _ps2 = [os.getenv('cephPrimaryStorageName2'), os.getenv('nfsPrimaryStorageName2')]
        self.ps_1_name = [pn for pn in _ps1 if pn][0]
        self.ps_2_name = [pn2 for pn2 in _ps2 if pn2][0]

    def get_image(self):
        conditions = res_ops.gen_query_conditions('name', '=', self.image_name_net)
        self.image = res_ops.query_resource(res_ops.IMAGE, conditions)[0]

    def get_ps(self):
        self.get_current_ps()
        cond = res_ops.gen_query_conditions('name', '=', self.ps_1_name)
        self.ps_1 = res_ops.query_resource(res_ops.PRIMARY_STORAGE, cond)[0]
        cond2 = res_ops.gen_query_conditions('name', '=', self.ps_2_name)
        self.ps_2 = res_ops.query_resource(res_ops.PRIMARY_STORAGE, cond2)[0]

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
        self._image.check()

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

