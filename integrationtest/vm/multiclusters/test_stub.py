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
import zstackwoodpecker.operations.volume_operations as vol_ops
import zstackwoodpecker.zstack_test.zstack_test_vm as test_vm_header
import zstackwoodpecker.header.host as host_header
import threading
import time
import sys
#import traceback


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

    def get_image(self):
        conditions = res_ops.gen_query_conditions('name', '=', self.image_name)
        self.image = res_ops.query_resource(res_ops.IMAGE, conditions)[0]

    def get_ps(self):
        if self.ceph_ps_name:
            conditions = res_ops.gen_query_conditions('name', '=', self.ceph_ps_name)
            self.ceph_ps = res_ops.query_resource(res_ops.PRIMARY_STORAGE, conditions)[0]
        if self.ceph_ps_name_2:
            conditions = res_ops.gen_query_conditions('name', '=', self.ceph_ps_name_2)
            self.ceph_ps_2 = res_ops.query_resource(res_ops.PRIMARY_STORAGE, conditions)[0]

    def get_bs(self):
        if self.ceph_bs_name:
            conditions = res_ops.gen_query_conditions('name', '=', self.ceph_bs_name)
            self.ceph_bs = res_ops.query_resource(res_ops.BACKUP_STORAGE, conditions)[0]
        if self.ceph_bs_name_2:
            conditions = res_ops.gen_query_conditions('name', '=', self.ceph_bs_name_2)
            self.ceph_bs_2 = res_ops.query_resource(res_ops.BACKUP_STORAGE, conditions)[0]

    def create_vm(self, image_name=None):
        if not image_name:
            image_name = self.image_name
        self.vm = create_vm('multicluster_basic_vm', image_name, os.getenv('l3VlanNetworkName1'))
        self.vm.check()
        self.root_vol_uuid = self.vm.vm.rootVolumeUuid

    def clone_vm(self):
        self.root_vol_uuid_list = []
        self.cloned_vms = self.vm.clone(['cloned-vm1', 'cloned-vm2'])
        for vm in self.cloned_vms:
            self.root_vol_uuid_list.append(vm.vm.rootVolumeUuid)

    def migrate_vm(self, cloned=False):
        self.dst_ps = self.get_ps_candidate()
        if not cloned:
            self.vm.stop()
            datamigr_ops.ps_migrage_root_volume(self.dst_ps.uuid, self.root_vol_uuid)
            conditions = res_ops.gen_query_conditions('uuid', '=', self.vm.vm.uuid)
            self.vm.vm = res_ops.query_resource(res_ops.VM_INSTANCE, conditions)[0]
            self.vm.start()
            self.vm.check()
            assert self.vm.vm.allVolumes[0].primaryStorageUuid == self.dst_ps.uuid
            self.root_vol_uuid = self.vm.vm.rootVolumeUuid
        else:
            for i in range(len(self.cloned_vms)):
                self.cloned_vms[i].stop()
                datamigr_ops.ps_migrage_root_volume(self.dst_ps.uuid, self.root_vol_uuid_list[i])
                conditions = res_ops.gen_query_conditions('uuid', '=', self.cloned_vms[i].vm.uuid)
                self.cloned_vms[i].vm = res_ops.query_resource(res_ops.VM_INSTANCE, conditions)[0]
                self.cloned_vms[i].start()
                self.cloned_vms[i].check()
                assert self.cloned_vms[i].vm.allVolumes[0].primaryStorageUuid == self.dst_ps.uuid

    def migrate_data_volume(self):
        if not self.dst_ps:
            self.dst_ps = self.get_ps_candidate()
        vol_migr_inv = datamigr_ops.ps_migrage_data_volume(self.dst_ps.uuid, self.data_volume.get_volume().uuid)
        cond_vol = res_ops.gen_query_conditions('uuid', '=', self.data_volume.get_volume().uuid)
        assert res_ops.query_resource(res_ops.VOLUME, cond_vol)
        self.data_volume_obsoleted = res_ops.query_resource(res_ops.VOLUME, cond_vol)[0]
        conditions = res_ops.gen_query_conditions('uuid', '=', vol_migr_inv.uuid)
        self.data_volume.set_volume(res_ops.query_resource(res_ops.VOLUME, conditions)[0])
        assert self.data_volume.get_volume().primaryStorageUuid == self.dst_ps.uuid

    def del_obsoleted_data_volume(self):
        vol_ops.delete_volume(self.data_volume_obsoleted.uuid)

    def migrate_image(self):
        self.get_image()
        dst_bs = self.get_bs_candidate()
        image_migr_inv = datamigr_ops.bs_migrage_image(dst_bs.uuid, self.image.backupStorageRefs[0].backupStorageUuid, self.image.uuid)
        condition_uuid = res_ops.gen_query_conditions('uuid', '=', self.image.uuid)
        assert res_ops.query_resource(res_ops.IMAGE, condition_uuid)
        condition_name = res_ops.gen_query_conditions('uuid', '=', image_migr_inv.uuid)
        self.image = res_ops.query_resource(res_ops.IMAGE, condition_name)[0]

    def create_image(self):
        bs = self.get_bs_candidate()
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

    def get_ps_candidate(self):
        self.cand_ps = datamigr_ops.get_ps_candidate_for_vol_migration(self.root_vol_uuid)
        assert len(self.cand_ps) == 1
        self.get_ps()
        ps_to_migrate = self.ceph_ps if self.ceph_ps.uuid != self.vm.vm.allVolumes[0].primaryStorageUuid else self.ceph_ps_2
        return ps_to_migrate

    def get_bs_candidate(self):
        self.get_image()
        self.cand_bs = datamigr_ops.get_bs_candidate_for_image_migration(self.image.backupStorageRefs[0].backupStorageUuid)
        assert len(self.cand_bs) == 1
        self.get_bs()
        bs_to_migrate = self.ceph_bs if self.ceph_bs.uuid != self.image.backupStorageRefs[0].backupStorageUuid else self.ceph_bs_2
        return bs_to_migrate

    def check_ps_candidate(self):
        ps_to_migrate = self.get_ps_candidate()
        assert self.cand_ps[0].uuid == ps_to_migrate.uuid

    def check_bs_candidate(self):
        bs_to_migrate = self.get_bs_candidate()
        assert self.cand_bs[0].uuid == bs_to_migrate.uuid

    def create_data_volume(self):
        conditions = res_ops.gen_query_conditions('name', '=', os.getenv('largeDiskOfferingName'))
        disk_offering_uuid = res_ops.query_resource(res_ops.DISK_OFFERING, conditions)[0].uuid
        volume_option = test_util.VolumeOption()
        volume_option.set_disk_offering_uuid(disk_offering_uuid)
        volume_option.set_name('data_volume_for_migration')
        volume_option.set_primary_storage_uuid(self.vm.vm.allVolumes[0].primaryStorageUuid)
        self.data_volume = create_volume(volume_option)
        self.data_volume.attach(self.vm)
