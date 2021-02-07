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
    print 'debug begin do netflow test'

#create netflow
    test_util.test_dsc("Create netflow")
    netflow = vpc_ops.create_flowmeter(type ='NetFlow', name='netflow', version = 'V9', port = 2000, description ='test netflow', server = vm_colloctor_ip)
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

    test_obj_dict.add_vm(vm_sender)
    test_obj_dict.add_vm(vm_colloctor)
#add vpc to netflow
    test_util.test_dsc("add vpc to netflow")
    vpc_ops.add_vpc_to_netflow(netflow_uuid, vr.inv.uuid, [vm_sender_l3_uuid])

#begin do test
    #test_stub.run_command_in_vm(vm_colloctor.get_vm(), 'iperf -s -D')
    print 'debug begin do netflow test'
    test_stub.run_command_in_vm(vm_sender.get_vm(), 'pkill iperf; iperf -c %s -i 1 -t 30 -P10 &' % vm_colloctor_ip)

#stop test after 500 seconds
    cmd = 'tshark -f "udp port 2000 and ip src %s " -i eth0 -V -c 1 -a duration:500' % vr_pub_ip
    print 'debug begin do netflow test cmd : %s' % cmd
    (retcode, output, erroutput) = ssh.execute(cmd , vm_colloctor_ip, 'root', 'password')
    print 'debug output is: %s' %output
    if vm_colloctor_ip in output and vr_pub_ip in output:
        test_util.test_dsc("Successfull capture the Cisco flow, test pass")
    else:
        test_util.test_fail("Failed capture the Cisco flow, test failed")

#delete netflow
    vpc_ops.delete_netflow(netflow_uuid, 'Permissive')
    test_util.test_pass("Capture the Cisco flow, test pass")

    test_lib.lib_error_cleanup(test_obj_dict)
    test_stub.remove_all_vpc_vrouter()


def env_recover():
    test_lib.lib_error_cleanup(test_obj_dict)
    test_stub.remove_all_vpc_vrouter()
