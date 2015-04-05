'''

@author: Youyk
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.net_operations as net_ops
import os

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def test():
    test_util.test_dsc('Repeat creating test vm in a limited ip range environment. If dnsmasq lease ip has bug, or zstack allocation ip has bug, it will meet failure.')
    l3_name = os.environ.get('l3VlanNetworkName4')
    condition = res_ops.gen_query_conditions('name', '=', l3_name)
    l3_net = res_ops.query_resource(res_ops.L3_NETWORK, condition)[0]
    ip_cap_evt = net_ops.get_ip_capacity_by_l3s([l3_net.uuid])
    if not ip_cap_evt:
        test_util.test_fail('can not get ip capability for l3: %s' % l3_name)

    avail_ips = ip_cap_evt.availableCapacity
    if avail_ips > 5:
        test_util.test_skip('l3: %s available ip address: %d is large than 5, which will bring a lot of testing burden. Suggest to reduce ip address setting and retest.' % (l3_name, avail_ips))

    while avail_ips > 0:
        vm = test_stub.create_vlan_vm(os.environ.get('l3VlanNetworkName4'))
        test_obj_dict.add_vm(vm)
        avail_ips -= 1
        test_util.test_logger('available ips: %d' % avail_ips)

    vm_list = list(test_obj_dict.get_vm_list())
    for vm in vm_list:
        avail_ips +=1
        test_util.test_logger('check No.%d vm' % avail_ips)
        vm.check()
        vm.destroy()
        test_obj_dict.rm_vm(vm)

    #after using all ip resource, create a new vm, which will use previous ip.
    vm = test_stub.create_vlan_vm(os.environ.get('l3VlanNetworkName4'))
    test_obj_dict.add_vm(vm)
    vm.check()
    vm.destroy()

    test_util.test_pass('Repeat Create VMs with limited ip range successfully.')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
