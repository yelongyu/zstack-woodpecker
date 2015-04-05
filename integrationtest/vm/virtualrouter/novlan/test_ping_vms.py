'''

@author: Frank
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def test():
    global test_obj_dict
    test_util.test_dsc('Create test vm1 and check')
    vm1 = test_stub.create_user_vlan_vm()
    test_obj_dict.add_vm(vm1)
    vm1.check()

    test_util.test_dsc('Create test vm2 and check')
    vm2 = test_stub.create_user_vlan_vm()
    test_obj_dict.add_vm(vm2)
    vm2.check()

    test_util.test_dsc('Ping from vm1 to vm2.')
    test_lib.lib_check_ping(vm1.vm, vm2.vm.vmNics[0].ip)
    vm1.destroy()
    vm2.destroy()
    test_util.test_pass('Create VirtualRouter VM Test with snat ping between two VMs Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)

