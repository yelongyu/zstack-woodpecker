'''

@author: SyZhao
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstacklib.utils.ssh as ssh
import os


test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()


def test():
    test_util.test_dsc('Create test vm and check')
    vm1 = test_stub.create_vm(vm_name="vm1", image_name="ocfs2-host-image")
    test_obj_dict.add_vm(vm1)

    vm2 = test_stub.create_vm(vm_name="vm2", image_name="ocfs2-host-image")
    test_obj_dict.add_vm(vm2)

    vm1.check()
    vm2.check()

    test_util.test_dsc('Create volume and check')
    disk_offering = test_lib.lib_get_disk_offering_by_name(os.environ.get('rootDiskOfferingName'))
    volume_creation_option = test_util.VolumeOption()
    volume_creation_option.set_disk_offering_uuid(disk_offering.uuid)
    volume_creation_option.set_system_tags(['ephemeral::shareable', 'capability::virtio-scsi'])

    vol_lst = []
    for i in xrange(24):

        volume = test_stub.create_volume(volume_creation_option)
        volume.check()
        test_obj_dict.add_volume(volume)
        vol_lst.append(volume)

        volume.attach(vm1)
        volume.attach(vm2)
        volume.check()

        volume.detach(vm1.get_vm().uuid)
        volume.detach(vm2.get_vm().uuid)
        volume.check()
    
    for vol in vol_lst:
        vol.delete()
        vol.expunge()
        vol.check()
        test_obj_dict.rm_volume(vol)

    vm1.destroy()
    vm2.destroy()
    vm1.check()
    vm2.check()
    vm1.expunge()
    vm2.expunge()
    test_util.test_pass('Create Max Sharable Volume for VM Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
