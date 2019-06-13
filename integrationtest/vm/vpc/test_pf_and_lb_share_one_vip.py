#coding:utf-8
'''

@author: yixin.wang

1.create 2 vpc_vrouter and attach l3 network 
2.create vm with different vpc vrouter network,vpc2 create 2 vm
3.create one vip for pf and lb
4.attach vm1_nic to pf and stop vm1 then attach vm2_nic to lb_listener(expected result is fail)
5.start vm1 and detach vm1_nic from pf then attach vm2_nic to lb_listener and pf(expected result is success)
6.clean resource
'''
from apibinding.api import ApiError
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.net_operations as net_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.zstack_test.zstack_test_load_balancer as zstack_lb_header
import zstackwoodpecker.zstack_test.zstack_test_port_forwarding as zstack_pf_header
import apibinding.inventory as inventory
import time
import os

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
PfRule = test_state.PfRule
Port = test_state.Port

vpc_name_list = ['vpc_test_1', 'vpc_test_2']
vpc_l3_list = ['l3VxlanNetwork11', 'l3VlanNetwork2']
vr_list = []
vm_list = []

def test():
    test_util.test_dsc("Create 2 vpc vrouter and attach l3 network to vpc")
    for i in [0, 1]:
        vr_list.append(test_stub.create_vpc_vrouter(vpc_name_list[i]))
        vpc_l3_uuid = test_lib.lib_get_l3_by_name(vpc_l3_list[i]).uuid
        test_stub.attach_l3_to_vpc_vr_by_uuid(vr_list[i], vpc_l3_uuid)

        test_util.test_dsc("Create 2 vm in vpc network")
        vm_list.append(test_stub.create_vm_with_random_offering(vm_name='vpc_vm_{}'.format(i), l3_name=vpc_l3_list[i]))
    	test_obj_dict.add_vm(vm_list[i])
    	vm_list[i].check()

    test_util.test_dsc("Create one vip for pf and lb")
    pub_net_uuid = test_lib.lib_find_vr_pub_nic(vr_list[0].inv).l3NetworkUuid
    vip = test_stub.create_vip('vip_test', pub_net_uuid)
    test_obj_dict.add_vip(vip)

    test_util.test_dsc("Create a pf and lb with vip")
    vip_uuid = vip.get_vip().uuid
    pub_net_ip = test_lib.lib_find_vr_pub_ip(vr_list[0].inv)
    pf_creation_opt = PfRule.generate_pf_rule_option(pub_net_ip, protocol=inventory.UDP, vip_target_rule=Port.rule1_ports,\
        private_target_rule=Port.rule1_ports, vip_uuid=vip_uuid, vm_nic_uuid=test_lib.lib_get_vm_last_nic(vm_list[0].get_vm()).uuid)
    pf = zstack_pf_header.ZstackTestPortForwarding()
    pf.set_creation_option(pf_creation_opt)
    pf.create(vm_list[0])
    lb = zstack_lb_header.ZstackTestLoadBalancer()
    lb.create('lb_test', vip_uuid)
    lb_creation_option = test_lib.lib_create_lb_listener_option()
    lb_listener = lb.create_listener(lb_creation_option)

    test_util.test_dsc("Attach vm1_nic to pf and attach vm2_nic to lb_listener")
    vip.attach_pf(pf)
    attach_nic2 = test_lib.lib_get_vm_last_nic(vm_list[1].get_vm())
    vm_list[0].stop()
    try:
        lb_listener.add_nics(['{}'.format(attach_nic2.uuid)])
    except ApiError, e:
        test_util.test_logger("Multi_network_service can not support different vrouter")

    test_util.test_dsc("Detach vm1_nic from pf and attach vm2_nic to pf")
    vm_list[0].start()
    time.sleep(10)
    pf.check()
    pf.detach()
    pf.attach(attach_nic2.uuid, vm_list[0])
    test_util.test_pass("Multi_network_service can support same vrouter")

    test_lib.lib_error_cleanup(test_obj_dict)
    test_stub.remove_all_vpc_vrouter()

def env_recover():
    test_lib.lib_error_cleanup(test_obj_dict)
    test_stub.remove_all_vpc_vrouter()

	
