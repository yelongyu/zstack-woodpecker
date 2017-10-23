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


def test():

    test_util.test_dsc("create vpc vrouter")

    vr_inv = test_stub.create_vpc_vrouter()

    test_util.test_dsc("Try to create one vm in random L3 not attached")
    with test_lib.expected_failure("create one vm in random L3 not attached", Exception):
        test_stub.create_vm_with_random_offering(vm_name='vpc_vm1', l3_name=random.choice(test_stub.L3_SYSTEM_NAME_LIST))

    test_util.test_dsc("attach vpc l3 to vpc vrouter")
    test_stub.attach_all_l3_to_vpc_vr(vr_inv, test_stub.L3_SYSTEM_NAME_LIST)

    test_util.test_dsc("Try to create one vm in random L3")
    vm1 = test_stub.create_vm_with_random_offering(vm_name='vpc_vm1', l3_name=random.choice(test_stub.L3_SYSTEM_NAME_LIST))
    test_obj_dict.add_vm(vm1)

    test_util.test_dsc("reboot VR and try to create vm in random L3")
    vm_ops.reboot_vm(vr_inv.uuid)
    vm2 = test_stub.create_vm_with_random_offering(vm_name='vpc_vm2', l3_name=random.choice(test_stub.L3_SYSTEM_NAME_LIST))
    test_obj_dict.add_vm(vm2)

    test_util.test_dsc("reconnect VR and try to create vm in random L3")
    vm_ops.reconnect_vr(vr_inv.uuid)
    vm3 = test_stub.create_vm_with_random_offering(vm_name='vpc_vm3', l3_name=random.choice(test_stub.L3_SYSTEM_NAME_LIST))
    test_obj_dict.add_vm(vm3)

    test_util.test_dsc("migrate VR and try to create vm in random L3")
    vm_ops.migrate_vm(vr_inv.uuid, random.choice([host.uuid for host in res_ops.get_resource(res_ops.HOST)
                                                  if host.uuid != test_lib.lib_find_host_by_vm(vr_inv).uuid]))
    vm4 = test_stub.create_vm_with_random_offering(vm_name='vpc_vm4', l3_name=random.choice(test_stub.L3_SYSTEM_NAME_LIST))
    test_obj_dict.add_vm(vm4)

    test_util.test_dsc("delete vr and try to create vm in random L3")
    vm_ops.destroy_vm(vr_inv.uuid)
    with test_lib.expected_failure('Create vpc vm when vpc l3 not attached', Exception):
        test_stub.create_vm_with_random_offering(vm_name='vpc_vm5', l3_name=random.choice(test_stub.L3_SYSTEM_NAME_LIST))

    test_lib.lib_error_cleanup(test_obj_dict)
    test_stub.remove_all_vpc_vrouter()


def env_recover():
    test_lib.lib_error_cleanup(test_obj_dict)
    test_stub.remove_all_vpc_vrouter()


