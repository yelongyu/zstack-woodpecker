'''

New Integration Test for creating 2 KVM VM on different 2l3 on same l2.

@author: Quarkonics
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.zstack_test.zstack_test_vm as test_vm_header
import time
import os

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def test():
    vm1 = test_stub.create_vlan_vm(os.environ.get('l3VlanNetworkName1'))
    test_obj_dict.add_vm(vm1)
    vm1.check()

    vm2 = test_stub.create_vlan_vm(os.environ.get('l3VlanNetworkName2'))
    test_obj_dict.add_vm(vm2)
    vm2.check()

    vm1.destroy()
    vm2.destroy()
    test_util.test_pass('Create 2VM different 2l3 on same l2 Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
