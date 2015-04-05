'''

@author: Youyk
'''
import os
import sys
import time
import threading

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.net_operations as net_ops

#can not do parallel testing.
_config_ = {
        'timeout' : 1200,
        'noparallel' : True
        }

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
exception=[]


def create_vm(l3_name):
    global test_obj_dict
    global exception
    try:
        vm = test_stub.create_vlan_vm(l3_name)
    except Exception as e:
        exception.append(sys.exc_info())
        raise e

    test_obj_dict.add_vm(vm)

def test():
    global exception
    test_util.test_dsc('Simutanously creating several test vm in a limited ip range environment. If zstack allocation IP has bug, vms might be assigned same IP addresses.')
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
        thread = threading.Thread(target=create_vm, \
                args=(os.environ.get('l3VlanNetworkName4'),))
        avail_ips -= 1
        test_util.test_logger('available ips: %d' % avail_ips)
        thread.start()

    while threading.activeCount() > 1:
        time.sleep(1)
        print('wait for vm creationg finished ...')

    if exception:
        print 'Meet exception when create VM'
        info1 = exception[0][1]
        info2 = exception[0][2]
        raise info1, None, info2

    vm_list = list(test_obj_dict.get_vm_list())
    ip_list = []
    for vm in vm_list:
        avail_ips +=1
        vm_ip = vm.get_vm().vmNics[0].ip
        if vm_ip in ip_list:
            test_util.test_fail('duplicate vm [ip] %s was found' % vm_ip)
        ip_list.append(vm_ip)

        test_util.test_logger('check No.%d vm; its ip is: %s' % (avail_ips, vm.get_vm().vmNics[0].ip))
        vm.check()
        vm.destroy()
        test_obj_dict.rm_vm(vm)

    test_util.test_pass('Repeat Create VMs with limited ip range successfully.')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
