'''
@author: FangSun
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.test_state as test_state
import random
import os
import zstackwoodpecker.operations.volume_operations as vol_ops
import time


flavor = dict(vm1_vm2_one_l3_vlan=dict(),
              vm1_vm2_one_l3_vxlan=dict(),
              vm1_l3_vlan_vm2_l3_vlan=dict(),
              vm1_l3_vxlan_vm2_l3_vxlan=dict(),
              vm1_l3_vlan_vm2_l3_vxlan=dict(),
              vm1_vm2_one_l3_vlan_migrate = dict(),
              vm1_l3_vlan_vm2_l3_vlan_migrate= dict(),
              vm1_l3_vxlan_vm2_l3_vxlan_vrreboot=dict(),
              )


test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def test():
    test_util.test_dsc("create vpc vrouter and attach vpc l3 to vpc")
    vr_inv = test_stub.create_vpc_vrouter()
    test_stub.attach_all_l3_to_vpc_vr(vr_inv)

    test_util.test_dsc("create two vm, vm1 in , vm2 in")

    test_util.test_dsc("test two vm connectivity")
