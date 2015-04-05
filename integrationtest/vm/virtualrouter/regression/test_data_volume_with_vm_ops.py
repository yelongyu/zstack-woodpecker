'''

Test VM ops result with data volume attached. 

@author: Youyk
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import os

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def test():
    test_util.test_dsc('Create test vm and check. ')
    vm = test_stub.create_vlan_vm()
    test_obj_dict.add_vm(vm)

    test_util.test_dsc('Create volume and check')
    disk_offering = test_lib.lib_get_disk_offering_by_name(os.environ.get('smallDiskOfferingName'))
    volume_creation_option = test_util.VolumeOption()
    volume_creation_option.set_disk_offering_uuid(disk_offering.uuid)

    volume1 = test_stub.create_volume(volume_creation_option)
    test_obj_dict.add_volume(volume1)
    volume2 = test_stub.create_volume(volume_creation_option)
    test_obj_dict.add_volume(volume2)

    test_util.test_dsc('Attach volume and check')
    volume1.attach(vm)
    volume2.attach(vm)
    volume1.check()
    volume2.check()

    test_util.test_dsc('Reboot VM and check')
    vm.reboot()
    volume1.check()
    volume2.check()

    test_util.test_dsc('stop/start VM and check')
    vm.stop()
    volume1.check()
    volume2.check()
    vm.start()
    volume1.check()
    volume2.check()

    vm.destroy()
    test_obj_dict.rm_vm(vm)

    volume1.delete()
    test_obj_dict.rm_volume(volume1)
    volume2.delete()
    test_obj_dict.rm_volume(volume2)

    test_util.test_pass('Attach Volume to VM with VM ops test pass')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
