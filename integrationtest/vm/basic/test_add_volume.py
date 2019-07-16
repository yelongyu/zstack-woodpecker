'''

@author: Youyk
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state

test_stub = test_lib.lib_get_specific_stub()

#test_obj_dict is to track test resource. They will be cleanup if there will be any exception in testing.
test_obj_dict = test_state.TestStateDict()

def test():
    global test_obj_dict

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

    test_util.test_dsc('Detach volume and check')
    volume.detach()
    volume.check()

    test_util.test_dsc('Delete volume and check')
    volume.delete()
    volume.check()
    test_obj_dict.rm_volume(volume)

    vm.destroy()
    vm.check()

    test_util.test_pass('Create Data Volume for VM Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)

