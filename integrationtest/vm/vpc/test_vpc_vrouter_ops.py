'''
@author: FangSun
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.resource_operations as res_ops
import time
import random


test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()


def test():

    test_util.test_dsc("create vpc vrouter")

    vr = test_stub.create_vpc_vrouter()
    test_util.test_dsc("Try to create one vm in random L3 not attached")
    with test_lib.expected_failure("create one vm in random L3 not attached", Exception):
        test_stub.create_vm_with_random_offering(vm_name='vpc_vm1', l3_name=random.choice(test_stub.L3_SYSTEM_NAME_LIST))

    test_util.test_dsc("attach vpc l3 to vpc vrouter")
    test_stub.attach_l3_to_vpc_vr(vr, test_stub.L3_SYSTEM_NAME_LIST)
    test_util.test_dsc("Try to create one vm in random L3")
    vm1 = test_stub.create_vm_with_random_offering(vm_name='vpc_vm1', l3_name=random.choice(test_stub.L3_SYSTEM_NAME_LIST))
    test_obj_dict.add_vm(vm1)
    vm1.check()

    test_util.test_dsc("reboot VR and try to create vm in random L3")
    vr.reboot()
    vm2 = test_stub.create_vm_with_random_offering(vm_name='vpc_vm2', l3_name=random.choice(test_stub.L3_SYSTEM_NAME_LIST))
    test_obj_dict.add_vm(vm2)
    vm2.check()

    test_util.test_dsc("stop VR and try to create vm in random L3")
    vr.stop()
    time.sleep(120) #wait 120 seconds and check the VR status
    conf = res_ops.gen_query_conditions('name', '=', 'test_vpc')
    vr_list = res_ops.query_resource(res_ops.APPLIANCE_VM, conf)[0]
    #vr_uuid = vr_list.uuid
    if vr_list.state == "Stopped" and vr_list.status == "Disconnected":
        test_util.test_dsc("stop VR sucessfully after wait 120 seconds.")
    else:
        test_util.test_fail('stop VR failed ,VR state : %s . VR status : %s .')%(vr_list.state, vr_list.status)

    test_util.test_dsc("start VR and try to create vm in random L3")
    vr.start()
    vm5 = test_stub.create_vm_with_random_offering(vm_name='vpc_vm2', l3_name=random.choice(test_stub.L3_SYSTEM_NAME_LIST))
    test_obj_dict.add_vm(vm5)
    vm5.check()

    test_util.test_dsc("reconnect VR and try to create vm in random L3")
    vr.reconnect()
    vm3 = test_stub.create_vm_with_random_offering(vm_name='vpc_vm3', l3_name=random.choice(test_stub.L3_SYSTEM_NAME_LIST))
    test_obj_dict.add_vm(vm3)
    vm3.check()

    test_util.test_dsc("migrate VR and try to create vm in random L3")
    vr.migrate_to_random_host()

    count = 0
    while vr.inv.state is 'Paused' and count < 10:
        vr.update()
        time.sleep(5)
        count += 1

    vm4 = test_stub.create_vm_with_random_offering(vm_name='vpc_vm4', l3_name=random.choice(test_stub.L3_SYSTEM_NAME_LIST))
    test_obj_dict.add_vm(vm4)
    vm4.check()

    test_util.test_dsc("delete vr and try to create vm in random L3")
    vr.destroy()
    with test_lib.expected_failure('Create vpc vm when vpc l3 not attached', Exception):
        test_stub.create_vm_with_random_offering(vm_name='vpc_vm5', l3_name=random.choice(test_stub.L3_SYSTEM_NAME_LIST))

    test_lib.lib_error_cleanup(test_obj_dict)
    test_stub.remove_all_vpc_vrouter()


def env_recover():
    test_lib.lib_error_cleanup(test_obj_dict)
    test_stub.remove_all_vpc_vrouter()

