'''
New Integration test for cold migration of data volume from template with snapshot between hosts.
@author: SyZhao
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.volume_operations as vol_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import apibinding.inventory as inventory
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.header.host as host_header
import zstackwoodpecker.zstack_test.zstack_test_image as zstack_image_header
import os

volume = None
vm = None
test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def test():
    global test_obj_dict
    #volume_creation_option = test_util.VolumeOption()
    #test_util.test_dsc('Create volume and check')
    #disk_offering = test_lib.lib_get_disk_offering_by_name(os.environ.get('smallDiskOfferingName'))
    #volume_creation_option.set_disk_offering_uuid(disk_offering.uuid)
    #volume = test_stub.create_volume(volume_creation_option)

    bs_cond = res_ops.gen_query_conditions("status", '=', "Connected")
    bss = res_ops.query_resource_fields(res_ops.BACKUP_STORAGE, bs_cond, \
            None, fields=['uuid'])
    if not bss:
        test_util.test_skip("not find available backup storage. Skip test")

    image_option = test_util.ImageOption()
    image_option.set_name('use_crt_data_vol')
    image_option.set_format('qcow2')
    image_option.set_mediaType('RootVolumeTemplate')
    image_option.set_url(os.environ.get('imageUrl_s'))
    image_option.set_backup_storage_uuid_list([bss[0].uuid])
    image_obj = zstack_image_header.ZstackTestImage()
    image_obj.set_creation_option(image_option)

    volume = test_lib.lib_create_data_volume_from_image(image_obj)
    test_obj_dict.add_volume(volume)
    volume.check()
    volume_uuid = volume.volume.uuid
    
    test_util.test_dsc('Create vm and check')
    vm = test_stub.create_vr_vm('migrate_volume_vm', 'imageName_s', 'l3VlanNetwork2')
    test_obj_dict.add_vm(vm)
    vm.check()
    vm_uuid = vm.vm.uuid
    
    ps = test_lib.lib_get_primary_storage_by_uuid(vm.get_vm().allVolumes[0].primaryStorageUuid)
    if ps.type != inventory.LOCAL_STORAGE_TYPE:
        test_util.test_skip('Skip test on non-localstorage')
    
    volume.attach(vm)
    volume.detach(vm_uuid)

    snapshots = test_obj_dict.get_volume_snapshot(volume_uuid)
    snapshots.set_utility_vm(vm)
    snapshots.create_snapshot('create_snapshot1')
    snapshots.check()
    snapshots.create_snapshot('create_snapshot2')
    snapshots.check()

    target_host = test_lib.lib_find_random_host_by_volume_uuid(volume_uuid)
    target_host_uuid = target_host.uuid

    vol_ops.migrate_volume(volume_uuid, target_host_uuid)

    test_lib.lib_error_cleanup(test_obj_dict)
    test_util.test_pass('Cold migrate Data Volume Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)
