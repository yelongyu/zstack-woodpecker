'''

A regression case to check if attach/detach operation can be successful on 
stopped VM.

@author: Youyk
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import os

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def test():
    test_util.test_dsc('Create test vm and check')
    vm = test_stub.create_vlan_vm()
    test_obj_dict.add_vm(vm)

    test_util.test_dsc('Create volume and check')
    disk_offering = test_lib.lib_get_disk_offering_by_name(os.environ.get('rootDiskOfferingName'))
    volume_creation_option = test_util.VolumeOption()
    volume_creation_option.set_disk_offering_uuid(disk_offering.uuid)

    volume = test_stub.create_volume(volume_creation_option)
    test_obj_dict.add_volume(volume)
    volume.check()

    test_util.test_dsc('Attach volume and check')
    vm.check()
    volume.attach(vm)
    volume.check()

    test_util.test_dsc('Stop VM')
    vm.stop()

    test_util.test_dsc('Detach volume and check')
    volume.detach()
    volume.check()

    test_util.test_dsc('Attach volume to stopped VM and check')
    volume.attach(vm)
    volume.check()

    test_util.test_dsc('Detach volume from stopped VM again and check')
    volume.detach()
    volume.check()

    volume2 = test_stub.create_volume(volume_creation_option)
    test_obj_dict.add_volume(volume2)
    test_util.test_dsc('Attach new volume2 to stopped VM and check')
    volume2.attach(vm)
    volume2.check()

    test_util.test_dsc('Detach volume2 from stopped VM again and check')
    volume2.detach()
    volume2.check()

    test_util.test_dsc('Attach new volume2 to stopped VM again and start vm')
    volume2.attach(vm)
    vm.start()
    test_util.test_dsc('Detach volume2 from running VM again and check')
    import time
    time.sleep(10)
    volume2.detach()
    volume2.check()

    test_util.test_dsc('Delete volume and check')
    volume.delete()
    volume.check()
    test_obj_dict.rm_volume(volume)
    volume2.delete()
    test_obj_dict.rm_volume(volume2)

    vm.destroy()
    test_util.test_pass('Do Volumes ops on stopped VM Success')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
