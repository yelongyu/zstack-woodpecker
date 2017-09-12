'''

New Integration Test for pf vip qos. 

@author: chenyuanxu
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.zstack_test.zstack_test_port_forwarding as zstack_pf_header
import apibinding.inventory as inventory
import zstackwoodpecker.operations.net_operations as net_ops
import zstacklib.utils.ssh as ssh
import time
import subprocess
import os

PfRule = test_state.PfRule
Port = test_state.Port
test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def exec_cmd_in_vm(vm, cmd, fail_msg):
    ret, output, stderr = ssh.execute(cmd, vm.get_vm().vmNics[0].ip, "root", "password", False, 22)
    if ret != 0:
        test_util.test_fail(fail_msg)
    return output

def test():
    vip_bandwidth = 1*1024
    pf_vm1 = test_stub.create_dnat_vm()
    test_obj_dict.add_vm(pf_vm1)
    pf_vm2 = test_stub.create_vlan_sg_vm()
    test_obj_dict.add_vm(pf_vm2)

    l3_name = os.environ.get('l3VlanNetworkName1')
    vr1 = test_stub.create_vr_vm(test_obj_dict, l3_name)

    vr1_pub_ip = test_lib.lib_find_vr_pub_ip(vr1)

    pf_vm1.check()
    pf_vm2.check()

    vm1_inv=pf_vm1.get_vm()
    vm2_inv=pf_vm2.get_vm()
    vm_nic1 = pf_vm1.vm.vmNics[0]
    vm_nic_uuid1 = vm_nic1.uuid
    pri_l3_uuid = vm_nic1.l3NetworkUuid
    vr = test_lib.lib_find_vr_by_l3_uuid(pri_l3_uuid)[0]
    vr_pub_nic = test_lib.lib_find_vr_pub_nic(vr)
    l3_uuid = vr_pub_nic.l3NetworkUuid
    vip = test_stub.create_vip('pf_attach_test', l3_uuid)
    test_obj_dict.add_vip(vip)
    vip_uuid = vip.get_vip().uuid
    vip_ip = vip.get_vip().ip

    #pf_creation_opt = PfRule.generate_pf_rule_option(vr1_pub_ip, protocol=inventory.TCP, vip_target_rule=Port.rule1_ports, private_target_rule=Port.rule1_ports)
    pf_creation_opt1 = PfRule.generate_pf_rule_option(vr1_pub_ip, protocol=inventory.TCP, vip_target_rule=Port.rule4_ports, private_target_rule=Port.rule4_ports, vip_uuid=vip_uuid)
    test_pf1 = zstack_pf_header.ZstackTestPortForwarding()
    test_pf1.set_creation_option(pf_creation_opt1)
    test_pf1.create()
    vip.attach_pf(test_pf1)
    pf_vm1.check()
    test_pf1.attach(vm_nic_uuid1, pf_vm1)
    vip_qos = net_ops.set_vip_qos(vip_uuid=vip_uuid, inboundBandwidth=vip_bandwidth*8*1024, outboundBandwidth=vip_bandwidth*8*1024)

    test_stub.make_ssh_no_password(vm1_inv)
    test_stub.make_ssh_no_password(vm2_inv)
    test_stub.install_iperf(vm1_inv)
    test_stub.install_iperf(vm2_inv)
    iptables_cmd = "iptables -F"
    exec_cmd_in_vm(pf_vm1, iptables_cmd, "Failed to clean iptables.")
    test_stub.test_iperf_bandwidth(vm1_inv,vm2_inv,vip_ip,20502,20502,vip_bandwidth)

    vip.delete()
    test_obj_dict.rm_vip(vip)
    pf_vm1.destroy()
    test_obj_dict.rm_vm(pf_vm1)
    pf_vm2.destroy()
    test_obj_dict.rm_vm(pf_vm2)

    test_util.test_pass("Test Port Forwarding Vip Qos Successfully.")

#Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)
