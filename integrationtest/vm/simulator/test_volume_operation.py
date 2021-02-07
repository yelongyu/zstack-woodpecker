'''

New Integration Test for creating KVM VM.

@author: Lei Liu
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import test_stub

def test():
    global vm
    vm = test_stub.create_vm()
    test_util.test_logger('Create VM Success')

    volume = test_stub.create_volume()
    test_util.test_logger('Create volume Success')

    volume.attach(vm)
    test_util.test_logger('attach volume Success')

    zone_uuid = vm.get_vm().zoneUuid
    bs_uuid_list = test_lib.lib_get_backup_storage_uuid_list_by_zone(zone_uuid)

    vol_template = test_stub.create_data_volume_template_from_volume(volume.get_volume().uuid, bs_uuid_list, "vol_temp_for_volume")
    
    imageUrl = test_stub.export_image_from_backup_storage(vol_template.uuid, bs_uuid_list[0])

    vol = test_stub.create_data_volume_from_template(vol_template.uuid, volume.get_volume().primaryStorageUuid, "vol_from_template", vm.get_vm().hostUuid)
    vol_uuid = vol.uuid
    test_util.test_logger('create volume from volume template Success')

    test_stub.delete_volume_image(vol_template.uuid)

    ps = test_lib.lib_get_primary_storage_by_uuid(volume.get_volume().primaryStorageUuid)

    if ps.type == 'LocalStorage':
         for host in test_stub.get_local_storage_volume_migratable_hosts(vol_uuid):
             test_stub.migrate_local_storage_volume(vol_uuid, host.uuid)
         test_stub.migrate_local_storage_volume(vol_uuid, vm.get_vm().hostUuid)


    test_lib.lib_attach_volume(vol_uuid, vm.get_vm().uuid)
    test_lib.lib_detach_volume(vol_uuid)

    test_stub.expunge_image(vol_template.uuid)

    if ps.type == 'LocalStorage':
         for host in test_stub.get_local_storage_volume_migratable_hosts(vol_uuid):
             test_stub.migrate_local_storage_volume(vol_uuid, host.uuid)

         test_stub.migrate_local_storage_volume(vol_uuid, vm.get_vm().hostUuid)
    test_lib.lib_attach_volume(vol_uuid, vm.get_vm().uuid)
    test_lib.lib_detach_volume(vol_uuid)
    test_stub.delete_volume(vol_uuid)

    test_stub.recover_volume(vol_uuid)
    if ps.type == 'LocalStorage':
         for host in test_stub.get_local_storage_volume_migratable_hosts(vol_uuid):
             test_stub.migrate_local_storage_volume(vol_uuid, host.uuid)

         test_stub.migrate_local_storage_volume(vol_uuid, vm.get_vm().hostUuid)
    
    test_lib.lib_attach_volume(vol_uuid, vm.get_vm().uuid)
    test_lib.lib_detach_volume(vol_uuid)
    vol_template = test_stub.create_data_volume_template_from_volume(volume.get_volume().uuid, bs_uuid_list, "vol_temp_for_volume")
    test_stub.delete_volume(vol_uuid)
    test_stub.expunge_volume(vol_uuid)

    #create volume again
    vol = test_stub.create_data_volume_from_template(vol_template.uuid, volume.get_volume().primaryStorageUuid, "vol_from_template", vm.get_vm().hostUuid)
    vol_uuid = vol.uuid
    test_util.test_logger('create volume from volume template Success')


#Will be called only if exception happens in test().
def error_cleanup():
    global vm
    if vm:
        vm.destroy()
