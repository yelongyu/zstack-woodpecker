
'''

New Integration Test for lb vip qos.

@author: chenyuanxu
'''
import os
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.zstack_test.zstack_test_load_balancer \
        as zstack_lb_header
import zstackwoodpecker.operations.net_operations as net_ops
import zstacklib.utils.ssh as ssh
import time
import subprocess
import os


test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def exec_cmd_in_vm(vm, cmd, fail_msg):
    ret, output, stderr = ssh.execute(cmd, vm.get_vm().vmNics[0].ip, "root", "password", False, 22)
    if ret != 0:
        test_util.test_fail(fail_msg)
    return output

def test():
    test_util.test_dsc('Create test vm with lb for LB different ports testing.')
    vip_bandwidth = 1*1024
    vm1 = test_stub.create_lb_vm()
    test_obj_dict.add_vm(vm1)
    vm2 = test_stub.create_lb_vm()
    test_obj_dict.add_vm(vm2)
    vm3 = test_stub.create_vlan_sg_vm()
    test_obj_dict.add_vm(vm3)

    vm1_inv=vm1.get_vm()
    vm3_inv=vm3.get_vm()
    vm_nic1 = vm1_inv.vmNics[0]
    vm_nic1_uuid = vm_nic1.uuid
    vm_nic2 = vm2_inv.vmNics[0]
    vm_nic2_uuid = vm_nic2.uuid
    pri_l3_uuid = vm_nic1.l3NetworkUuid

    vr = test_lib.lib_find_vr_by_l3_uuid(pri_l3_uuid)[0]
    vr_pub_nic = test_lib.lib_find_vr_pub_nic(vr)
    l3_uuid = vr_pub_nic.l3NetworkUuid

    vip = test_stub.create_vip('vip_for_lb_test', l3_uuid)
    test_obj_dict.add_vip(vip)
    vip_uuid = vip.get_vip().uuid
    vip_ip = vip.get_vip().ip
    vip_qos = net_ops.set_vip_qos(vip_uuid=vip_uuid, inboundBandwidth=vip_bandwidth*8*1024, outboundBandwidth=vip_bandwidth*8*1024)

    lb = zstack_lb_header.ZstackTestLoadBalancer()
    lb.create('create lb test', vip.get_vip().uuid)
    test_obj_dict.add_load_balancer(lb)

    lb_creation_option = test_lib.lib_create_lb_listener_option(lbl_port = 5001, lbi_port = 5001 )

    lbl = lb.create_listener(lb_creation_option)

    lbl.add_nics([vm_nic1_uuid, vm_nic2_uuid])
    vm1.check()
    vm2.check()
    lb.check()

    test_stub.make_ssh_no_password(vm1_inv)
    test_stub.make_ssh_no_password(vm3_inv)
    test_stub.install_iperf(vm1_inv)
    test_stub.install_iperf(vm3_inv)
    iptables_cmd = "iptables -F"
    exec_cmd_in_vm(vm1, iptables_cmd, "Failed to clean iptables.")
    test_stub.test_iperf_bandwidth(vm1_inv,vm3_inv,vip_ip,5001,5001,vip_bandwidth)
    
    test_lib.lib_robot_cleanup(test_obj_dict)
    test_util.test_pass('Test Load Balancer VIP Qos Success')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
