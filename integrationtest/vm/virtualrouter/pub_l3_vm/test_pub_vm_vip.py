'''

@author: FangSun
'''


import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.operations.net_operations as net_ops


test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()


def test():

    pub_l3_vm, flat_l3_vm, vr_l3_vm = test_stub.generate_pub_test_vm(tbj=test_obj_dict)

    ip_status_before = net_ops.get_ip_capacity_by_l3s(l3_network_list=[pub_l3_vm.get_vm().vmNics[0].l3NetworkUuid])

    with test_lib.expected_failure('Create VIP with Pub vm IP', Exception):
        test_stub.create_vip(vip_name='test_vip', required_ip=pub_l3_vm.get_vm().vmNics[0].ip)

    ip_status_after = net_ops.get_ip_capacity_by_l3s(l3_network_list=[pub_l3_vm.get_vm().vmNics[0].l3NetworkUuid])

    assert ip_status_before.availableCapacity == ip_status_after.availableCapacity

    test_vip = test_stub.create_vip('test_vip')
    test_obj_dict.add_vip(test_vip)

    ip_status_final = net_ops.get_ip_capacity_by_l3s(l3_network_list=[pub_l3_vm.get_vm().vmNics[0].l3NetworkUuid])

    assert ip_status_final.availableCapacity == ip_status_after.availableCapacity - 1

    test_util.test_pass('pub vm volume network test pass')


def env_recover():
    test_lib.lib_error_cleanup(test_obj_dict)
