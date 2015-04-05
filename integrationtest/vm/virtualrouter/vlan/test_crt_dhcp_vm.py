'''

@author: Youyk
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import os

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def test():
    test_util.test_dsc('Create test vm and check. VR only has DHCP services')
    vm = test_stub.create_vlan_vm(os.environ.get('l3VlanNetworkName5'))
    test_obj_dict.add_vm(vm)
    vm.check()

    vm.destroy()
    test_util.test_pass('Create VirtualRouter VM with DHCP Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
