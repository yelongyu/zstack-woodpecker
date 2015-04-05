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
    '''
    Test Description:
        Will create 1 no virtual router VM. And 2 Virtual Router VMs with diffferent Virutal Router. After virutal router VM created, will check virtual router vm network connection to external network.
    Resource required:
        Need support 5 VMs existing at the same time. 
    '''
    vm1 = test_stub.create_vlan_vm()
    test_obj_dict.add_vm(vm1)

    vm2 = test_stub.create_user_vlan_vm()
    test_obj_dict.add_vm(vm2)

    vm3 = test_stub.create_basic_vm()
    test_obj_dict.add_vm(vm3)

    vm1.check()
    vm2.check()
    vm3.check()

    vm1.destroy()
    vm2.destroy()
    vm3.destroy()
    test_util.test_pass('Create 1 vlan and 1 novlan VirtualRouter VM + 1 None VirutalRouter VM Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
