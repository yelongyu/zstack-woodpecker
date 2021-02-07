'''
@author: FangSun
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import os
import zstackwoodpecker.zstack_test.zstack_test_port_forwarding as zstack_pf_header
import apibinding.inventory as inventory
from itertools import izip


VLAN1_NAME, VLAN2_NAME = ['l3VlanNetworkName1', "l3VlanNetwork2"]
VXLAN1_NAME, VXLAN2_NAME = ["l3VxlanNetwork11", "l3VxlanNetwork12"]
CLASSIC_L3 = 'l3NoVlanNetworkName2'

vpc1_l3_list = [VLAN1_NAME, VLAN2_NAME]
vpc2_l3_list = [VXLAN1_NAME, VXLAN2_NAME]

vpc_l3_list = [vpc1_l3_list, vpc2_l3_list]
vpc_name_list = ['vpc1','vpc2']


case_flavor = dict(vm1_vm2_one_vpc_1vlan=   dict(vm1l3=VLAN1_NAME, vm2l3=VLAN1_NAME, one_vpc=True),
                   vm1_vm2_one_vpc_2vlan=   dict(vm1l3=VLAN1_NAME, vm2l3=VLAN2_NAME, one_vpc=True),
                   vm1_vm2_two_vpc=         dict(vm1l3=VLAN1_NAME, vm2l3=VXLAN2_NAME, one_vpc=False),
                   vm1_classic_vm2_vpc  =   dict(vm1l3=VXLAN2_NAME, vm2l3=CLASSIC_L3, one_vpc=False)
                   )

PfRule = test_state.PfRule
Port = test_state.Port
test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
vr_list = []


def test():
    flavor = case_flavor[os.environ.get('CASE_FLAVOR')]
    test_util.test_dsc("create vpc vrouter and attach vpc l3 to vpc")
    for vpc_name in vpc_name_list:
        vr_list.append(test_stub.create_vpc_vrouter(vpc_name))
    for vr, l3_list in izip(vr_list, vpc_l3_list):
        test_stub.attach_l3_to_vpc_vr(vr, l3_list)

    test_util.test_dsc("create two vm, vm1 in l3 {}, vm2 in l3 {}".format(flavor['vm1l3'], flavor['vm2l3']))
    vm1 = test_stub.create_vm_with_random_offering(vm_name='vpc_vm_{}'.format(flavor['vm1l3']), l3_name=flavor['vm1l3'])
    test_obj_dict.add_vm(vm1)
    vm1.check()
    vm2 = test_stub.create_vm_with_random_offering(vm_name='vpc_vm_{}'.format(flavor['vm2l3']), l3_name=flavor['vm2l3'])
    test_obj_dict.add_vm(vm2)
    vm2.check()

    vr_pub_nic = None
    test_util.test_dsc("create testing vpc vm")
    tmp_vr = test_stub.create_vpc_vrouter('test_vpc')
    for nic in tmp_vr.inv.vmNics:
        if nic.metaData == "2":    #2 means management /public net seprate; 3 means management /public net use the same
            vr_pub_nic = nic
            break

    test_util.test_dsc("Create vip")
    vip = test_stub.create_vip('vip1', vr_pub_nic.l3NetworkUuid)
    test_obj_dict.add_vip(vip)

    pf_creation_opt = PfRule.generate_pf_rule_option(vr_pub_nic.ip, protocol=inventory.TCP, vip_target_rule=Port.rule4_ports, private_target_rule=Port.rule4_ports, vip_uuid=vip.get_vip().uuid)
    test.pf = zstack_pf_header.ZstackTestPortForwarding()
    test.pf.set_creation_option(pf_creation_opt)
    test.pf.create()
    vip.attach_pf(test.pf)

    vip.check()

    if flavor['one_vpc']:
        for vm in (vm1,vm2):
            test.pf.attach(vm.get_vm().vmNics[0].uuid, vm)
            vm.check()
            vip.check()
            test.pf.detach()
            vm.check()
            vip.check()
    else:
        test.pf.attach(vm1.get_vm().vmNics[0].uuid, vm1)
        vm1.check()
        vip.check()
        test.pf.detach()
        vm1.check()
        vip.check()
        test.pf.delete()
        pf_creation_opt = PfRule.generate_pf_rule_option(vr_pub_nic.ip, protocol=inventory.TCP, vip_target_rule=Port.rule4_ports, private_target_rule=Port.rule4_ports, vip_uuid=vip.get_vip().uuid)
        test.pf = zstack_pf_header.ZstackTestPortForwarding()
        test.pf.set_creation_option(pf_creation_opt)
        test.pf.create()
        vip.attach_pf(test.pf)
        vip.check()
        test.pf.attach(vm2.get_vm().vmNics[0].uuid, vm2)
        vm2.check()
        vip.check()
        test.pf.detach()
        vm2.check()
        vip.check()
        
    test.pf.delete()

    test_lib.lib_error_cleanup(test_obj_dict)
    test_stub.remove_all_vpc_vrouter()


def env_recover():
    with test_lib.ignored(AttributeError):
        test.pf.delete()
    test_lib.lib_error_cleanup(test_obj_dict)
    test_stub.remove_all_vpc_vrouter()

