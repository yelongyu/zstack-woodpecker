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
import time
import os

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

vpc_name_list = ['vpc_test_1', 'vpc_test_2']
vpc_l3_list = ['l3VxlanNetwork11', 'l3VlanNetwork2']
vr_list = []
vm_list = []

def test():
    test_util.test_dsc("Create 2 vpc vrouter and attach l3 network to vpc")
    for i in [0, 1]:
        vr_list.append(test_stub.create_vpc_vrouter(vpc_name_list[i]))
        test_util.test_logger(vpc_l3_list[i])
        test_util.test_logger(test_stub.L3_SYSTEM_NAME_LIST)
        vpc_l3_uuid = test_lib.lib_get_l3_by_name(vpc_l3_list[i]).uuid
	    test_stub.attach_l3_to_vpc_vr_by_uuid(vr_list[i], vpc_l3_uuid)
        test_util.test_dsc("Create 2 vm in vpc network")
        vm_list.append(test_stub.create_vm_with_random_offering(vm_name='vpc_vm_{}'.format(i), l3_name=vpc_l3_list[i]))
        test_obj_dict.add_vm(vm_list[i])
        vm_list[i].check()

    test_util.test_dsc("Create one vip for lb")
    pub_net_uuid = test_lib.lib_find_vr_pub_nic(vr_list[0].inv).l3NetworkUuid
    vip = test_stub.create_vip('vip_test', pub_net_uuid)
    test_obj_dict.add_vip(vip)

    test_util.test_dsc("Create lb and lb_listener")
    vip_uuid = vip.get_vip().uuid
    lb = zstack_lb_header.ZstackTestLoadBalancer()
    lb.create('lb_test', vip_uuid)
    lb_creation_option = test_lib.lib_create_lb_listener_option()
    lb_listener = lb.create_listener(lb_creation_option)

    test_util.test_dsc("Add nic to lb_listener and detach nic then add another nic")
    attach_nic = test_lib.lib_get_vm_last_nic(vm_list[0].get_vm())
    lb_listener.add_nics(['{}'.format(attach_nic.uuid)])
    vm_list[0].remove_nic(attach_nic.uuid)

    time.sleep(10)
    attach_nic = test_lib.lib_get_vm_last_nic(vm_list[1].get_vm())
    lb_listener.add_nics(['{}'.format(attach_nic.uuid)])

    test_util.test_pass('Vip can be release when vm_nic was detached!')
    test_lib.lib_error_cleanup(test_obj_dict)
    test_stub.remove_all_vpc_vrouter()

def env_recover():
    test_lib.lib_error_cleanup(test_obj_dict)
    test_stub.remove_all_vpc_vrouter()

