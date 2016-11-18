'''
Test vr default name format
@author: SyZhao
'''


import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.resource_operations as res_ops


test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
vr_l3_name_prefix = "VirtualRouter.l3"

def test():
    test_util.test_dsc('Test vr default name format')
    vm = test_stub.create_basic_vm()
    test_obj_dict.add_vm(vm)

    vm.check()

    vr_inv = test_lib.lib_find_vr_by_vm(vm.vm)[0]
    actual_name = vr_inv.name #VirtualRouter.l3.l3VlanNetwork3

    guest_l3network_uuid = vr_inv.vmNics[0].l3NetworkUuid
    guest_l3network_name = test_lib.lib_get_l3_by_uuid(guest_l3network_uuid).name
    guest_l3network_uuid_head_6_num = guest_l3network_uuid[0:6]

    expected_name = vr_l3_name_prefix + "." + guest_l3network_name + "." + guest_l3network_uuid_head_6_num

    if expected_name != actual_name:
        #test_util.test_logger("Test vr default name is not the same as expected, actual name:%s, expected name: %s" %(actual_name, expected_name))
        test_util.test_fail("Test vr default name is not the same as expected, actual name:%s, expected name: %s" %(actual_name, expected_name))


    vm.destroy()

    test_util.test_pass('Test vr default name format success.')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
