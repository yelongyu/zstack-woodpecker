'''
@author: FangSun
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.vm_operations as vm_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.net_operations as net_ops
import time
import random
import os
from itertools import izip



test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()


case_flavor = dict(reboot_vr=       dict(reboot=True, reconnect=False),
                   reconnect_vr=    dict(reboot=False, reconnect=True),
                   )



def test():
    flavor = case_flavor[os.environ.get('CASE_FLAVOR')]
    test_util.test_dsc("create vpc vrouter and attach vpc l3 to vpc")
    vr = test_stub.create_vpc_vrouter()
    test_stub.attach_l3_to_vpc_vr(vr)

    vm = test_stub.create_vm_with_random_offering(vm_name='vpc_vm', l3_name=random.choice(test_stub.L3_SYSTEM_NAME_LIST))
    test_obj_dict.add_vm(vm)
    vm.check()

    for _ in xrange(3):
        if flavor['reboot']:
            vr.reboot()
        elif flavor['reconnect']:
            vr.reconnect()
    vm.check()

    test_lib.lib_error_cleanup(test_obj_dict)
    test_stub.remove_all_vpc_vrouter()

def env_recover():
    test_lib.lib_error_cleanup(test_obj_dict)
    test_stub.remove_all_vpc_vrouter()

