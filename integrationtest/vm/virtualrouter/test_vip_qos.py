'''

New Integration Test for set vip qos.

@author: chenyuanxu
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.resource_operations as res_ops
import apibinding.inventory as inventory
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
    vip_bandwidth = 1*1024
    vm1 = test_stub.create_vlan_vm(os.environ.get('l3VlanNetworkName1'))
    test_obj_dict.add_vm(vm1)
    vm1.check()
    vm1_nic = vm1.vm.vmNics[0]
    vm1_nic_uuid = vm1_nic.uuid
    pri_l3_uuid1 = vm1.vm.vmNics[0].l3NetworkUuid
    vr1 = test_lib.lib_find_vr_by_l3_uuid(pri_l3_uuid1)[0]
    l3_uuid1 = test_lib.lib_find_vr_pub_nic(vr1).l3NetworkUuid
    vip1 = test_stub.create_vip('qos_vip', l3_uuid1)
    test_obj_dict.add_vip(vip1)
    eip1 = test_stub.create_eip('create qos test', vip_uuid=vip1.get_vip().uuid, vnic_uuid=vm1_nic_uuid, vm_obj=vm1)
    vip1.attach_eip(eip1)
    vip1_ip = vip1.get_vip().ip
    vip1_qos = net_ops.set_vip_qos(vip_uuid=vip1.get_vip().uuid, inboundBandwidth=vip_bandwidth*8*1024, outboundBandwidth=vip_bandwidth*8*1024)

    vm2 = test_stub.create_vlan_vm(os.environ.get('l3VlanDNATNetworkName'))
    test_obj_dict.add_vm(vm2)
    vm2.check()
    vm2_nic = vm2.vm.vmNics[0]
    vm2_nic_uuid = vm2_nic.uuid
    pri_l3_uuid2 = vm2.vm.vmNics[0].l3NetworkUuid
    vr2 = test_lib.lib_find_vr_by_l3_uuid(pri_l3_uuid2)[0]
    l3_uuid2 = test_lib.lib_find_vr_pub_nic(vr2).l3NetworkUuid
    vip2 = test_stub.create_vip('qos_vip', l3_uuid2)
    test_obj_dict.add_vip(vip2)
    eip2 = test_stub.create_eip('create qos test', vip_uuid=vip2.get_vip().uuid, vnic_uuid=vm2_nic_uuid, vm_obj=vm2)
    vip2.attach_eip(eip2)
    vip2_ip = vip2.get_vip().ip

    vm1_inv = vm1.get_vm()
    vm2_inv = vm2.get_vm()
    test_stub.make_ssh_no_password(vm1_inv)
    test_stub.make_ssh_no_password(vm2_inv)
    test_stub.install_iperf(vm1_inv)
    test_stub.install_iperf(vm2_inv)
    iptables_cmd = "iptables -F"
    exec_cmd_in_vm(vm1, iptables_cmd, "Failed to clean iptables.")
    exec_cmd_in_vm(vm2, iptables_cmd, "Failed to clean iptables.")
    test_stub.test_iperf_bandwidth(vm1_inv,vm2_inv,vip1_ip,5001,5001,vip_bandwidth)
    test_stub.test_iperf_bandwidth(vm2_inv,vm1_inv,vip2_ip,5001,5001,vip_bandwidth)

    test_lib.lib_error_cleanup(test_obj_dict)
    test_util.test_pass('Create VIP Qos for EIP Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global mevoco1_ip
    global mevoco2_ip
    os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP'] = mevoco1_ip
    global test_obj_dict1
    test_lib.lib_error_cleanup(test_obj_dict1)


    os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP'] = mevoco2_ip
    global test_obj_dict2
    test_lib.lib_error_cleanup(test_obj_dict2)
