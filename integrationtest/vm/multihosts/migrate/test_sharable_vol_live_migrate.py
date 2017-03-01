'''

@author: SyZhao
'''
import apibinding.inventory as inventory
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstacklib.utils.ssh as ssh
import os


test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()


def test():
    test_util.test_dsc('Create test vm and check')

    if not test_lib.lib_check_version_is_mevoco():
        test_util.test_skip("Current version is not mevoco, skip!")

    vm1 = test_stub.create_vr_vm('vm1', 'imageName_net', 'l3VlanNetwork3')
    test_obj_dict.add_vm(vm1)

    backup_storage_list = test_lib.lib_get_backup_storage_list_by_vm(vm1.vm)
    for bs in backup_storage_list:
        #if bs.type == inventory.IMAGE_STORE_BACKUP_STORAGE_TYPE:
        #    break
        #if bs.type == inventory.SFTP_BACKUP_STORAGE_TYPE:
        #    break
        if bs.type == inventory.CEPH_BACKUP_STORAGE_TYPE:
            break
    else:
        vm1.destroy()
        test_util.test_skip('Not find ceph type backup storage.')

    vm2 = test_stub.create_vr_vm('vm2', 'imageName_net', 'l3VlanNetwork3')
    test_obj_dict.add_vm(vm2)

    test_util.test_dsc('Create volume and check')
    disk_offering = test_lib.lib_get_disk_offering_by_name(os.environ.get('largeDiskOfferingName'))
    volume_creation_option = test_util.VolumeOption()
    volume_creation_option.set_disk_offering_uuid(disk_offering.uuid)
    volume_creation_option.set_system_tags(['ephemeral::shareable', 'capability::virtio-scsi'])

    volume = test_stub.create_volume(volume_creation_option)
    test_obj_dict.add_volume(volume)
    volume.check()

    test_util.test_dsc('Attach volume and check')
    #mv vm checker later, to save some time.
    vm1.check()
    vm2.check()
    volume.attach(vm1)
    volume.attach(vm2)
    volume.check()
    
    test_stub.migrate_vm_to_random_host(vm1)
    vm1.check()
    volume.check()

    test_stub.migrate_vm_to_random_host(vm2)
    vm2.check()
    volume.check()

    test_util.test_dsc('Detach volume and check')
    volume.detach(vm1.get_vm().uuid)
    volume.detach(vm2.get_vm().uuid)
    volume.check()

    test_util.test_dsc('Delete volume and check')
    volume.delete()
    volume.expunge()
    volume.check()
    test_obj_dict.rm_volume(volume)

    vm1.destroy()
    vm2.destroy()
    vm1.check()
    vm2.check()
    vm1.expunge()
    vm2.expunge()
    test_util.test_pass('Create Data Volume for VM Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
