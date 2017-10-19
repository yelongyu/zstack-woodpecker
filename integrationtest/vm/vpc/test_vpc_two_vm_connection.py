'''
@author: FangSun
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.vm_operations as vm_ops
import random
import os
import zstackwoodpecker.operations.volume_operations as vol_ops
import time


VLAN1_NAME, VLAN2_NAME = ['l3VlanNetworkName1', "l3VlanNetwork3"]
VXLAN1_NAME, VXLAN2_NAME = ["l3VxlanNetwork11", "l3VxlanNetwork12"]

case_flavor = dict(vm1_vm2_one_l3_vlan=               dict(vm1l3=VLAN1_NAME, vm2l3=VLAN1_NAME, migrate=False, vrreboot=False),
                   vm1_vm2_one_l3_vxlan=              dict(vm1l3=VXLAN1_NAME, vm2l3=VXLAN1_NAME, migrate=False, vrreboot=False),
                   vm1_l3_vlan_vm2_l3_vlan=           dict(vm1l3=VLAN1_NAME, vm2l3=VLAN2_NAME, migrate=False, vrreboot=False),
                   vm1_l3_vxlan_vm2_l3_vxlan=         dict(vm1l3=VXLAN1_NAME, vm2l3=VXLAN2_NAME, migrate=False, vrreboot=False),
                   vm1_l3_vlan_vm2_l3_vxlan=          dict(vm1l3=VLAN1_NAME, vm2l3=VXLAN1_NAME, migrate=False, vrreboot=False),
                   vm1_vm2_one_l3_vlan_migrate=       dict(vm1l3=VLAN1_NAME, vm2l3=VLAN1_NAME, migrate=True, vrreboot=False),
                   vm1_l3_vlan_vm2_l3_vlan_migrate=   dict(vm1l3=VLAN1_NAME, vm2l3=VLAN2_NAME, migrate=True, vrreboot=False),
                   vm1_l3_vxlan_vm2_l3_vxlan_vrreboot=dict(vm1l3=VXLAN1_NAME, vm2l3=VXLAN2_NAME, migrate=False, vrreboot=True),
                   )


test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()


def test():
    flavor = case_flavor[os.environ.get('CASE_FLAVOR')]
    test_util.test_dsc("create vpc vrouter and attach vpc l3 to vpc")
    vr_inv = test_stub.create_vpc_vrouter()
    time.sleep(30)
    test_stub.attach_all_l3_to_vpc_vr(vr_inv)

    test_util.test_dsc("create two vm, vm1 in l3 {}, vm2 in l3 {}".format(flavor['vm1l3'], flavor['vm2l3']))
    vm1, vm2 = [test_stub.create_vm_with_random_offering(vm_name='vpc_vm_{}'.format(name), l3_name=name) for name in (flavor['vm1l3'], flavor['vm2l3']) ]

    for vm in (vm1, vm2):
        test_obj_dict.add_vm(vm)
        vm.check()

    if flavor['migrate']:
        test_stub.migrate_vm_to_random_host(vm2)
        vm2.check()

    if flavor['vrreboot']:
        vm_ops.reboot_vm(vr_inv.uuid)

    vm1_inv = vm1.get_vm()
    vm2_inv = vm2.get_vm()

    test_util.test_dsc("test two vm connectivity")
    test_lib.lib_check_ping(vm1_inv, vm2_inv.vmNics[0].ip)
    test_lib.lib_check_ping(vm2_inv, vm1_inv.vmNics[0].ip)

    test_lib.lib_check_ports_in_a_command(vm1_inv, vm1_inv.vmNics[0].ip,
                                          vm2_inv.vmNics[0].ip, test_stub.target_ports, [], vm2_inv)

    test_lib.lib_check_ports_in_a_command(vm2_inv, vm2_inv.vmNics[0].ip,
                                          vm1_inv.vmNics[0].ip, test_stub.target_ports, [], vm1_inv)

def env_recover():
    test_lib.lib_error_cleanup(test_obj_dict)
