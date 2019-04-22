'''

New case for EIP NS gateway leak to vm in same l3 network

@author: Hengguo.Ge
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.host_operations as host_ops
import os
import time
import zstacklib.utils.ssh as ssh

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

ext_host_ip = "172.20.1.106"
ext_host_pwd = "zstack.org"


def test():
    test_util.test_dsc('Create test vm with EIP and check.')
    vm1 = test_stub.create_vlan_vm(os.environ.get('l3VlanNetworkName1'))
    test_obj_dict.add_vm(vm1)

    vm2 = test_stub.create_vlan_vm(os.environ.get('l3VlanNetworkName1'))
    test_obj_dict.add_vm(vm2)

    pri_l3_name = os.environ.get('l3VlanNetworkName1')
    pri_l3_uuid = test_lib.lib_get_l3_by_name(pri_l3_name).uuid

    pub_l3_name = os.environ.get('l3PublicNetworkName')
    pub_l3_uuid = test_lib.lib_get_l3_by_name(pub_l3_name).uuid

    vm1_nic = vm1.vm.vmNics[0]
    vm1_nic_uuid = vm1_nic.uuid

    vm2_nic = vm2.vm.vmNics[0]
    vm2_nic_uuid = vm2_nic.uuid

    [test_stub.run_command_in_vm(vm.get_vm(), 'iptables -F') for vm in (vm1, vm2)]

    vip = test_stub.create_vip('create_eip_test', pub_l3_uuid)
    vip_ip = vip.get_vip().ip
    test_obj_dict.add_vip(vip)
    eip = test_stub.create_eip('create eip test', vip_uuid=vip.get_vip().uuid, vnic_uuid=vm1_nic_uuid, vm_obj=vm1)

    vip.attach_eip(eip)

    vm1.check()

    pri_l3_gateway = os.environ.get('vlanIpRangeGateway1')

    cmd1 = "ping -c 5 %s" % (vip_ip)
    (retcode1, output1, erroutput1) = ssh.execute(cmd1, ext_host_ip, "root", ext_host_pwd, True, 22)
    print "retcode1 is: %s; output1 is : %s.; erroutput1 is: %s" % (retcode1, output1, erroutput1)

    cmd2 = "arp -n | grep -w %s" % (pri_l3_gateway)
    if test_lib.lib_execute_command_in_flat_vm(vm2.vm, cmd2, l3_uuid=pri_l3_uuid):
        vm1.destroy()
        vm2.destroy()
        vm1.expunge()
        vm2.expunge()
        eip.delete()
        vip.delete()
        test_util.test_fail('Gateway leak to other vm, test failed.')

    vm1.destroy()
    vm2.destroy()
    vm1.expunge()
    vm2.expunge()
    eip.delete()
    vip.delete()


# Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)