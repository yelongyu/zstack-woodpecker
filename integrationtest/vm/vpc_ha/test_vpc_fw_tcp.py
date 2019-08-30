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

#create sender
    vm_sender = test_stub.create_vm('vm_sender', 'image_with_network_tools', 'l3VxlanNetwork11')
    vm_sender.check()
    vm_sender_ip = vm_sender.get_vm().vmNics[0].ip
    vm_sender_l3_uuid = vm_sender.get_vm().vmNics[0].l3NetworkUuid
    test_obj_dict.add_vm(vm_sender)

# Create firewall
    fw = vpc_ops.create_firewall(vr.inv.uuid, 'test_fw', 'firewall for test')
# Create rule set
    rs = vpc_ops.create_rule_set(fw.uuid, 'test_rule_set', 'accept', 'rule set for test')
# Create rule
    rule = vpc_ops.create_rule(fw.uuid, rs.uuid, 'drop', 1200, 'enable', protocol = 'TCP')
# Attach rule set to l3
    vpc_ops.AttachFirewallRuleSetToL3(fw.uuid, vm_sender_l3_uuid, 'out', rs.uuid)

#create iperf server
    iperf_server = test_stub.create_vm('iperf_server', 'image_with_network_tools', 'l3VxlanNetwork12')
    iperf_server.check()
    iperf_server_ip = iperf_server.get_vm().vmNics[0].ip
    test_util.test_dsc("iperf server ip is: %s" % iperf_server_ip)
    test_obj_dict.add_vm(iperf_server)

# Begin to do test
    cmd = 'pkill iperf; iperf -c %s -i 1 -t 5' % vm_sender_ip
    print 'debug begin do test cmd : %s' % cmd
    (retcode, output, erroutput) = ssh.execute(cmd , iperf_server_ip, 'root', 'password')
    print 'debug output is: %s' %output
    if "Mbits" in output or "Gbits" in output:
        test_util.test_fail("Firewall don't work ,except iperf can't connect server, test failed")
    else:
        test_util.test_dsc("Firewall worked, test pass")

    vpc_ops.DetachFirewallRuleSetFromL3(fw.uuid, vm_sender_l3_uuid, 'out')
##delete firewall resource
    vpc_ops.DeleteFirewallRule(rule.uuid, 'Permissive')
    vpc_ops.DeleteFirewallRuleSet(rs.uuid, 'Permissive')
    vpc_ops.DeleteFirewall(fw.uuid, 'Permissive')
    test_util.test_pass("Firewall works well, test pass")

    test_lib.lib_error_cleanup(test_obj_dict)
    test_stub.remove_all_vpc_vrouter()

def env_recover():
    test_lib.lib_error_cleanup(test_obj_dict)
    test_stub.remove_all_vpc_vrouter()
