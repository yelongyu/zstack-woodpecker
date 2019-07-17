'''

@author: Frank
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state

test_stub = test_lib.lib_get_specific_stub()

#test_obj_dict is to track test resource. They will be cleanup if there will be any exception in testing.
test_obj_dict = test_state.TestStateDict()

vm = None

def test():
    '''
    Test Description:
        Test add volume with negative test.
    Resource required:
        2 test VMs with additional 1*10M data volume.

    '''
    test_util.test_dsc('Create test vm and check')
    vm = test_stub.create_vm()
    test_obj_dict.add_vm(vm)
    vm.check()

    test_util.test_dsc('Create volume and check')
    volume = test_stub.create_volume()
    test_obj_dict.add_volume(volume)
    volume.check()

    test_util.test_dsc('Attach volume and check')
    volume.attach(vm)
    volume.check()

    test_util.test_dsc('Doing negative test. Try to reattach same volume to vm again.')
    try:
        volume.attach(vm)
    except:
        test_util.test_logger('Catch expected exception. [volume:] %s can not be attached to [vm:] %s twice.' % (volume.volume.uuid, vm.vm.uuid))
        test_util.test_dsc('Doing negative test. Try to delete an attached data volume.')
        vm2 = test_stub.create_vm()
        test_obj_dict.add_vm(vm2)
        test_util.test_dsc('Doing negative test. Try to attach an attached volume to 2nd vm.')
        try:
            volume.attach(vm2)
        except:
            test_util.test_logger('Catch expected exception. [volume:] %s can not be attached to another [vm:] %s, as it is already attached to [vm:] %s.' % (volume.volume.uuid, vm2.vm.uuid, vm.vm.uuid))
            volume.check()
            try:
                volume.delete()
            except:
                test_util.test_fail('Catch wrong logic: [volume:] %s can not be deleted, when it is assigned to [vm:] %s' % (volume.volume.uuid, vm.vm.uuid))
            test_obj_dict.rm_volume(volume)
            vm.destroy()
            test_obj_dict.rm_vm(vm)
            vm2.destroy()
            test_obj_dict.rm_vm(vm2)
            volume.check()
            test_util.test_pass('Data Volume Negative Test Success')
            return True

        test_util.test_fail('Catch wrong logic: [volume:] %s is attached to [vm:] %s again, although it is already attached to [vm:] %s .' % (volume.volume.uuid, vm2.vm.uuid, vm.vm.uuid))
    test_util.test_fail('Catch wrong logic: [volume:] %s is attached to [vm:] %s twice.' % (volume.volume.uuid, vm.vm.uuid))

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)

