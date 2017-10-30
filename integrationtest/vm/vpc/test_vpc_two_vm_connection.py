'''
@author: FangSun
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.vm_operations as vm_ops
import zstackwoodpecker.operations.host_operations as host_ops
import random
import os
import zstackwoodpecker.operations.volume_operations as vol_ops
import time


VLAN1_NAME, VLAN2_NAME = ['l3VlanNetworkName1', "l3VlanNetwork3"]
VXLAN1_NAME, VXLAN2_NAME = ["l3VxlanNetwork11", "l3VxlanNetwork12"]


VM_REBOOT='vm_reboot'
VM_MIGRATE= 'vm_migrate'
VR_MIGRATE= 'vr_migrate'
VR_REBOOT = 'vr_reboot'
VR_RECONNECT = 'vr_reconnect'
HOST_RECONNECT = 'host_reconnect'


case_flavor = dict(vm1_vm2_one_l3_vlan=               dict(vm1l3=VLAN1_NAME, vm2l3=VLAN1_NAME, ops=None),
                   vm1_vm2_one_l3_vxlan=              dict(vm1l3=VXLAN1_NAME, vm2l3=VXLAN1_NAME, ops=None),
                   vm1_l3_vlan_vm2_l3_vlan=           dict(vm1l3=VLAN1_NAME, vm2l3=VLAN2_NAME, ops=None),
                   vm1_l3_vxlan_vm2_l3_vxlan=         dict(vm1l3=VXLAN1_NAME, vm2l3=VXLAN2_NAME, ops=None),
                   vm1_l3_vlan_vm2_l3_vxlan=          dict(vm1l3=VLAN1_NAME, vm2l3=VXLAN1_NAME, ops=None),
                   vm1_vm2_one_l3_vlan_migrate=       dict(vm1l3=VLAN1_NAME, vm2l3=VLAN1_NAME, ops=VM_MIGRATE),
                   vm1_l3_vlan_vm2_l3_vlan_migrate=   dict(vm1l3=VLAN1_NAME, vm2l3=VLAN2_NAME, ops=VM_MIGRATE),
                   vm1_l3_vxlan_vm2_l3_vxlan_vrreboot=dict(vm1l3=VXLAN1_NAME, vm2l3=VXLAN2_NAME, ops=VR_REBOOT),
                   vm1_l3_vxlan_vm2_l3_vxlan_vmreboot=dict(vm1l3=VXLAN1_NAME, vm2l3=VXLAN2_NAME, ops=VM_REBOOT),
                   vm1_l3_vlan_vm2_l3_vlan_vrreconnect= dict(vm1l3=VLAN1_NAME, vm2l3=VLAN2_NAME, ops=VR_RECONNECT),
                   vm1_l3_vlan_vm2_l3_vlan_vr_migrate= dict(vm1l3=VLAN1_NAME, vm2l3=VLAN2_NAME, ops=VR_MIGRATE),
                   vm1_l3_vlan_vm2_l3_vxlan_hostreconnect= dict(vm1l3=VLAN1_NAME, vm2l3=VXLAN1_NAME, ops=HOST_RECONNECT),
                   )


test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()


def test():
    flavor = case_flavor[os.environ.get('CASE_FLAVOR')]
    test_util.test_dsc("create vpc vrouter and attach vpc l3 to vpc")
    vr_inv = test_stub.create_vpc_vrouter()
    test_stub.attach_l3_to_vpc_vr(vr_inv)

    test_util.test_dsc("create two vm, vm1 in l3 {}, vm2 in l3 {}".format(flavor['vm1l3'], flavor['vm2l3']))
    vm1 = test_stub.create_vm_with_random_offering(vm_name='vpc_vm_{}'.format(flavor['vm1l3']), l3_name=flavor['vm1l3'])
    test_obj_dict.add_vm(vm1)
    vm1.check()
    vm2 = test_stub.create_vm_with_random_offering(vm_name='vpc_vm_{}'.format(flavor['vm2l3']), l3_name=flavor['vm2l3'])
    test_obj_dict.add_vm(vm2)
    vm2.check()


    if flavor['ops'] is VM_MIGRATE:
        test_stub.migrate_vm_to_random_host(vm2)
        vm2.check()
    elif flavor['ops'] is VM_REBOOT:
        vm1.reboot()
        vm1.check()
    elif flavor['ops'] is VR_REBOOT:
        vm_ops.reboot_vm(vr_inv.uuid)
        time.sleep(10)
    elif flavor['ops'] is VR_RECONNECT:
        vm_ops.reconnect_vr(vr_inv.uuid)
        time.sleep(10)
    elif flavor['ops'] is VR_MIGRATE:
        vm_ops.migrate_vm(vr_inv.uuid, random.choice([host.uuid for host in res_ops.get_resource(res_ops.HOST)
                                                      if host.uuid != test_lib.lib_find_host_by_vm(vr_inv).uuid]))
    elif flavor['ops'] is HOST_RECONNECT:
        host = test_lib.lib_find_host_by_vm(vm1.get_vm())
        host_ops.reconnect_host(host.uuid)
        time.sleep(10)

    if flavor['ops'] is not None:
        for vm in (vm1,vm2):
            vm.check()

    vm1_inv = vm1.get_vm()
    vm2_inv = vm2.get_vm()

    test_util.test_dsc("test two vm connectivity")
    test_stub.run_command_in_vm(vm1_inv, 'iptables -F')
    test_stub.run_command_in_vm(vm2_inv, 'iptables -F')

    test_lib.lib_check_ping(vm1_inv, vm2_inv.vmNics[0].ip)
    test_lib.lib_check_ping(vm2_inv, vm1_inv.vmNics[0].ip)

    test_lib.lib_check_ports_in_a_command(vm1_inv, vm1_inv.vmNics[0].ip,
                                          vm2_inv.vmNics[0].ip, ["22"], [], vm2_inv)

    test_lib.lib_check_ports_in_a_command(vm2_inv, vm2_inv.vmNics[0].ip,
                                          vm1_inv.vmNics[0].ip, ["22"], [], vm1_inv)

    test_lib.lib_error_cleanup(test_obj_dict)
    test_stub.remove_all_vpc_vrouter()

def env_recover():
    test_lib.lib_error_cleanup(test_obj_dict)
    test_stub.remove_all_vpc_vrouter()
