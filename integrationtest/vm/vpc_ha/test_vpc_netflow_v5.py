'''
@author: Pengtao.Zhang
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.vpc_operations as vpc_ops
import os
from itertools import izip
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.vm_operations as vm_ops
import zstackwoodpecker.operations.host_operations as host_ops
import random
import time
import apibinding.api_actions as api_actions
import subprocess
import zstacklib.utils.ssh as ssh


VPC1_VLAN, VPC1_VXLAN = ['l3VlanNetwork2', "l3VxlanNetwork12"]
VPC2_VLAN, VPC2_VXLAN = ["l3VlanNetwork3", "l3VxlanNetwork13"]

vpc_l3_list = [(VPC1_VLAN, VPC1_VXLAN), (VPC2_VLAN, VPC2_VXLAN)]

case_flavor = dict(vm1_l3_vlan_vm2_l3_vlan=dict(vm1l3=VPC1_VLAN, vm2l3=VPC2_VLAN),
                   vm1_l3_vxlan_vm2_l3_vxlan=dict(vm1l3=VPC1_VXLAN, vm2l3=VPC2_VXLAN),
                   vm1_l3_vlan_vm2_l3_vxlan=dict(vm1l3=VPC1_VLAN, vm2l3=VPC2_VXLAN),
                   )

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

@test_lib.pre_execution_action(test_stub.remove_all_vpc_vrouter)
def test():
    test_util.test_dsc("create vpc vrouter and attach vpc l3 to vpc")
    vr = test_stub.create_vpc_vrouter()
    test_stub.attach_l3_to_vpc_vr(vr)
    conf = res_ops.gen_query_conditions('name', '=', 'test_vpc')
    vr_nics = res_ops.query_resource(res_ops.APPLIANCE_VM, conf)[0].vmNics
    for nic in vr_nics:
        if '172.2' in nic.ip:
            vr_pub_ip = nic.ip
    test_util.test_dsc("VPC public ip is: %s" % vr_pub_ip)
    print 'debug vr_pub_ip: %s' % vr_pub_ip
#create colloctor
    vm_colloctor = test_stub.create_vm('vm_colloctor', 'image_with_network_tools', 'public network')
    vm_colloctor.check()
    vm_colloctor_ip = vm_colloctor.get_vm().vmNics[0].ip
    test_util.test_dsc("Netflow colloctor ip is: %s" % vm_colloctor_ip)
#create netflow
    test_util.test_dsc("Create netflow")
    netflow = vpc_ops.create_flowmeter(type ='NetFlow', name='netflow', description ='test netflow', server = vr_pub_ip)
    netflow_uuid = netflow.uuid
    print 'debug netflow_uuid ; %s' % netflow_uuid
    print 'debug vm_colloctor_ip: %s' % vm_colloctor_ip
#create sender
    vm_sender = test_stub.create_vm('vm_sender', 'image_with_network_tools', 'l3VlanNetwork1')
    vm_sender.check()
    vm_sender_ip = vm_sender.get_vm().vmNics[0].ip
    vm_sender_l3_uuid = vm_sender.get_vm().vmNics[0].l3NetworkUuid
    print 'debug vm_sender_l3_uuidis: %s' %vm_sender_l3_uuid
    print 'debug vr.inv.uuid: %s' %vr.inv.uuid
#add vpc to netflow
    test_util.test_dsc("add vpc to netflow")
    vpc_ops.add_vpc_to_netflow(netflow_uuid, vr.inv.uuid, [vm_sender_l3_uuid])
#begin do test
    test_stub.run_command_in_vm(vm_colloctor.get_vm(), 'iperf -s -D')
    test_stub.run_command_in_vm(vm_sender.get_vm(), 'iperf -c %s -i 1 -t 20 &' % vm_colloctor_ip)
    cmd = 'tshark -f "udp port 2055 and ip src %s " -i eth0 -V -c 1' % vr_pub_ip
    (retcode, output, erroutput) = ssh.execute(cmd , vm_colloctor_ip, 'root', 'password')
    print 'debug output is: %s' %output

#    vm1, vm2 = [test_stub.create_vm_with_random_offering(vm_name='vpc_vm_{}'.format(name), l3_name=name) for name in
#                (flavor['vm1l3'], flavor['vm2l3'])]

#    [test_obj_dict.add_vm(vm) for vm in (vm1, vm2)]
#    [vm.check() for vm in (vm1, vm2)]

#    test_util.test_dsc("test two vm connectivity")
#    [test_stub.run_command_in_vm(vm.get_vm(), 'iptables -F') for vm in (vm1, vm2)]
#
#    test_stub.check_icmp_connection_to_public_ip(vm1, expected_result='PASS')
#    test_stub.check_icmp_connection_to_public_ip(vm2, expected_result='PASS')

#    test_util.test_dsc("disable snat")
#    for vr in vr_list:
#        vr_uuid = vr.inv.uuid
#        vpc_ops.set_vpc_vrouter_network_service_state(vr_uuid, networkService='SNAT', state='disable')
#    test_stub.check_icmp_connection_to_public_ip(vm1, expected_result='FAIL')
#    test_stub.check_icmp_connection_to_public_ip(vm2, expected_result='FAIL')

#    test_lib.lib_error_cleanup(test_obj_dict)
#    test_stub.remove_all_vpc_vrouter()


def env_recover():
#    test_lib.lib_error_cleanup(test_obj_dict)
#    test_stub.remove_all_vpc_vrouter()
	pass
