'''

@author: Youyk
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def test():
    global test_obj_dict
    test_util.test_dsc('Create test vm with Vlan SR and check')
    vm = test_stub.create_vlan_vm()
    test_obj_dict.add_vm(vm)
    vm.check()
    test_util.test_dsc('Reboot vm and check again')
    vm.stop()
    vm.check()
    vm.start()
    vm.check()

    vm.destroy()
    test_util.test_pass('Vlan VR VM reboot Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)
