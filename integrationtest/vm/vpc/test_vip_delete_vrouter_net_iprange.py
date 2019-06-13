#coding:utf-8
'''

@author: yixin.wang
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.net_operations as net_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.zstack_test.zstack_test_load_balancer as zstack_lb_header
import random
import time
import os

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

vrouter_network = 'l3NoVlanNetworkName2'
vm_list = []

def test():
    test_util.test_dsc("Create a vm with vrouter_network")
    vm_list.append(test_stub.create_vm_with_random_offering(vm_name='vrouter_test', l3_name=vrouter_network))
    test_obj_dict.add_vm(vm_list[0])
    vm_list[0].check()

    test_util.test_dsc("Create vpc vrouter and attach l3 netwotk")
    vr = test_stub.create_vpc_vrouter('vpc_router_test')
    test_stub.attach_l3_to_vpc_vr(vr, test_stub.L3_SYSTEM_NAME_LIST)
    vm_list.append(test_stub.create_vm_with_random_offering(vm_name='vpc_vm', l3_name=random.choice(test_stub.L3_SYSTEM_NAME_LIST)))
    test_obj_dict.add_vm(vm_list[1])
    vm_list[1].check()

    test_util.test_dsc("Create one vip for lb")
    pub_net_uuid = test_lib.lib_find_vr_pub_nic(vr.inv).l3NetworkUuid
    vip = test_stub.create_vip('vip_test', pub_net_uuid)
    test_obj_dict.add_vip(vip)

    test_util.test_dsc("Create lb and lb_listener")
    vip_uuid = vip.get_vip().uuid
    lb = zstack_lb_header.ZstackTestLoadBalancer()
    lb.create('lb_test', vip_uuid)
    lb_creation_option = test_lib.lib_create_lb_listener_option()
    lb_listener = lb.create_listener(lb_creation_option)

    test_util.test_dsc("Add vrouter_test_nic to listener and delete ip range of vrouter_network")
    attach_nic = test_lib.lib_get_vm_last_nic(vm_list[0].get_vm())
    lb_listener.add_nics(['{}'.format(attach_nic.uuid)])	

    cond = res_ops.gen_query_conditions('name', '=', os.environ.get(vrouter_network))
    vrouter_l3 = res_ops.query_resource(res_ops.L3_NETWORK, cond)[0]
    vrouter_l3_uuid = vrouter_l3.ipRanges[0].uuid 
    net_ops.delete_ip_range(vrouter_l3_uuid)

    test_util.test_dsc("Add vpc vm nic to listener")
    attach_nic = test_lib.lib_get_vm_last_nic(vm_list[1].get_vm())
    lb_listener.add_nics(['{}'.format(attach_nic.uuid)])
    test_util.test_pass('Vip can be realase when vrouter_network ip range was deleted!')

    test_lib.lib_error_cleanup(test_obj_dict)
    test_stub.remove_all_vpc_vrouter()

def env_recover():
    test_lib.lib_error_cleanup(test_obj_dict)
    test_stub.remove_all_vpc_vrouter()	




