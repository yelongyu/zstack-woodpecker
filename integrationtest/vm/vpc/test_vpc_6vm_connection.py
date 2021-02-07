'''
@author: FangSun
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import random

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()




def test():
    test_util.test_dsc("create vpc vrouter and attach vpc l3 to vpc")
    vr = test_stub.create_vpc_vrouter('vpc1')
    test_stub.all_vpc_l3_list.remove('l3NoVlanNetworkName1')
    l3_list = random.sample(test_stub.all_vpc_l3_list, 6)
    test_stub.attach_l3_to_vpc_vr(vr, l3_list)

    vm_list = []
    for l3_name in l3_list:
        vm = test_stub.create_vm_with_random_offering(vm_name='vpc_vm_{}'.format(l3_name), l3_name=l3_name)
        test_obj_dict.add_vm(vm)
        vm_list.append(vm)

    for vm in vm_list:
        vm.check()

    test_util.test_dsc("random get two vms and check the connectivity")
    for _ in range(10):
        vm1, vm2 = random.sample(vm_list, 2)
        test_util.test_dsc("test two vm connectivity")
        [test_stub.run_command_in_vm(vm.get_vm(), 'iptables -F') for vm in (vm1,vm2)]

        test_stub.check_icmp_between_vms(vm1, vm2, expected_result='PASS')
        test_stub.check_tcp_between_vms(vm1, vm2, ["22"], [])

    test_lib.lib_error_cleanup(test_obj_dict)
    test_stub.remove_all_vpc_vrouter()


def env_recover():
    test_lib.lib_error_cleanup(test_obj_dict)
    test_stub.remove_all_vpc_vrouter()
