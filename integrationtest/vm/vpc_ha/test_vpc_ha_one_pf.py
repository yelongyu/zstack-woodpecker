'''
@author: yixin.wang
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import os
import zstackwoodpecker.zstack_test.zstack_test_port_forwarding as zstack_pf_header
import apibinding.inventory as inventory
from itertools import izip
import time


VLAN1_NAME, VLAN2_NAME = ['l3VlanNetworkName1', "l3VlanNetwork2"]
VXLAN1_NAME, VXLAN2_NAME = ["l3VxlanNetwork11", "l3VxlanNetwork12"]
VLAN3_NAME, VXLAN3_NAME = ["l3VlanNetwork5", "l3VxlanNetwork15"]
CLASSIC_L3 = 'l3NoVlanNetworkName2'

vpc1_l3_list = [VLAN1_NAME, VLAN2_NAME]
vpc2_l3_list = [VXLAN1_NAME, VXLAN2_NAME]
vpc3_l3_list = [VLAN3_NAME, VXLAN3_NAME]

vpc_l3_list = [vpc1_l3_list, vpc2_l3_list]
vpc_ha_group_name_list = ['test_vpc_ha', 'test_vpc_ha_upgrade']
ha_group_vpc_name_list = ['vpc-test','vpc-test-peer']
ha_monitor_ip = ['192.168.0.1']
vpc_name_list = ['vpc1','vpc2']


case_flavor = dict(vm1_vm2_one_vpc_1vlan=   dict(vm1l3=VLAN1_NAME, vm2l3=VLAN1_NAME, one_vpc=True, ha=False, upgrade=False),
                   vm1_vm2_one_vpc_2vlan=   dict(vm1l3=VLAN1_NAME, vm2l3=VLAN2_NAME, one_vpc=True, ha=False, upgrade=False),
                   vm1_vm2_two_vpc=         dict(vm1l3=VLAN1_NAME, vm2l3=VXLAN2_NAME, one_vpc=False, ha=False, upgrade=False),
                   vm1_classic_vm2_vpc  =   dict(vm1l3=VXLAN2_NAME, vm2l3=CLASSIC_L3, one_vpc=False, ha=False, upgrade=False),
                   vm1_ha_vm2_ha_one_vpc_1vlan_1vxlan=   dict(vm1l3=VLAN3_NAME, vm2l3=VXLAN3_NAME, one_vpc=True, ha=True, upgrade=False),
                   vm1_ha_vm2_noha_two_vpc=   dict(vm1l3=VXLAN3_NAME, vm2l3=VLAN2_NAME, one_vpc=False, ha=True, upgrade=False),
                   vm1_ha_vm2_noha_upgrade_two_vpc=   dict(vm1l3=VLAN3_NAME, vm2l3=VXLAN2_NAME, one_vpc=False, ha=True, upgrade=True),
                   vm1_ha_classic_vm2_vpc=   dict(vm1l3=VXLAN3_NAME, vm2l3=CLASSIC_L3, one_vpc=False, ha=True, upgrade=False)
                   )

PfRule = test_state.PfRule
Port = test_state.Port
test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
ha_group_list = []
ha_vr_list = []
vr_list = []
vm_list = []

@test_lib.pre_execution_action(test_stub.remove_all_vpc_ha_group)
@test_lib.pre_execution_action(test_stub.remove_all_vpc_vrouter)

def ha_group_resource():
    test_util.test_dsc("create vpc ha group and new vpc vrouter then attach l3 and create vm")
    for ha_group_name in vpc_ha_group_name_list:
        ha_group_list.append(test_stub.create_vpc_ha_group(ha_group_name, ha_monitor_ip))
    
    for ha_vpc_name in ha_group_vpc_name_list:
        ha_vr_list.append(test_stub.create_vpc_vrouter_with_tags(ha_vpc_name, tags='haUuid::{}'.format(ha_group_list[0].uuid)))
    time.sleep(10)
    test_stub.add_dns_to_ha_vpc(ha_vr_list[0].inv.uuid)
    test_stub.attach_l3_to_vpc_vr(ha_vr_list[0], vpc3_l3_list)

def vpc_resource():
    test_util.test_dsc("create vpc vrouter and attach vpc l3 to vpc")
    for vpc_name in vpc_name_list:
        vr_list.append(test_stub.create_vpc_vrouter(vpc_name))
    for vr, l3_list in izip(vr_list, vpc_l3_list):
        test_stub.attach_l3_to_vpc_vr(vr, l3_list)

def vpc_ha_pf_check(vm, vip, pf, groupUuid):
    test.pf.attach(vm.get_vm().vmNics[0].uuid, vm)
    vm.check()
    vip.check()
    test_stub.update_ha_status(groupUuid)
    test_stub.check_ha_status(groupUuid)
    vm.check()
    vip.check()
    pf.detach()
    vm.check()
    vip.check()

def vpc_pf_check(vm, vip, pf):
    test.pf.attach(vm.get_vm().vmNics[0].uuid, vm)
    vm.check()
    vip.check()
    pf.detach()
    vm.check()
    vip.check()

def test():
    flavor = case_flavor[os.environ.get('CASE_FLAVOR')]
    if flavor['ha']:
        ha_group_resource()

    vpc_resource()
    test_util.test_dsc("create two vm, vm1 in l3 {}, vm2 in l3 {}".format(flavor['vm1l3'], flavor['vm2l3']))
    vm1 = test_stub.create_vm_with_random_offering(vm_name='vpc_vm_{}'.format(flavor['vm1l3']), l3_name=flavor['vm1l3'])
    test_obj_dict.add_vm(vm1)
    vm1.check()
    vm2 = test_stub.create_vm_with_random_offering(vm_name='vpc_vm_{}'.format(flavor['vm2l3']), l3_name=flavor['vm2l3'])
    test_obj_dict.add_vm(vm2)
    vm2.check()

    vr_pub_nic = None
    test_util.test_dsc("create testing vpc vm")
    tmp_vr = test_stub.create_vpc_vrouter('vpc-for-pf-test')
    for nic in tmp_vr.inv.vmNics:
        if nic.metaData == "1":    #1 means management /public net seprate; 3 means management /public net use the same
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
        test_util.test_dsc("test one pf for one vpc vrouter")
        if flavor['ha']:
            test_util.test_dsc("test one pf for ha_vpc vrouter")
            for vm in (vm1,vm2):
                vpc_ha_pf_check(vm1, vip, test.pf, ha_group_list[0].uuid)
                vpc_ha_pf_check(vm2, vip, test.pf, ha_group_list[0].uuid)
        test_util.test_dsc("test one pf for one no_ha_vpc vrouter")
        for vm in (vm1,vm2):
            vpc_pf_check(vm1, vip, test.pf)
            vpc_pf_check(vm2, vip, test.pf)

    elif flavor['ha']:
        if flavor['upgrade']:
            test_util.test_dsc("upgrade vpc2 to ha vpc")
            vr_list[1].stop()
            vr_list[1].start_with_tags(tags='haUuid::{}'.format(ha_group_list[1].uuid))
            ha_vr_list.append(vr_list[1])
            ha_vr_list.append(test_stub.create_vpc_vrouter_with_tags(vr_name='{}-peer'.format(vpc_name_list[1]), tags='haUuid::{}'.format(ha_group_list[1].uuid)))
            vpc_ha_pf_check(vm1, vip, test.pf, ha_group_list[0].uuid)
            test.pf.delete()
            pf_creation_opt = PfRule.generate_pf_rule_option(vr_pub_nic.ip, protocol=inventory.TCP, vip_target_rule=Port.rule4_ports, private_target_rule=Port.rule4_ports, vip_uuid=vip.get_vip().uuid)
            test.pf = zstack_pf_header.ZstackTestPortForwarding()
            test.pf.set_creation_option(pf_creation_opt)
            test.pf.create()
            vip.attach_pf(test.pf)
            vip.check()
        else:
            test_util.test_dsc("test one pf for two vpc vrouter")
            vpc_ha_pf_check(vm1, vip, test.pf, ha_group_list[0].uuid)
            test.pf.delete()
            pf_creation_opt = PfRule.generate_pf_rule_option(vr_pub_nic.ip, protocol=inventory.TCP, vip_target_rule=Port.rule4_ports, private_target_rule=Port.rule4_ports, vip_uuid=vip.get_vip().uuid)
            test.pf = zstack_pf_header.ZstackTestPortForwarding()
            test.pf.set_creation_option(pf_creation_opt)
            test.pf.create()
            vip.attach_pf(test.pf)
            vip.check()
            vpc_pf_check(vm2, vip, test.pf)
    else :
        test_util.test_dsc("test one pf for two no_ha_vpc vrouter")
        vpc_pf_check(vm1, vip, test.pf)
        test.pf.delete()
        pf_creation_opt = PfRule.generate_pf_rule_option(vr_pub_nic.ip, protocol=inventory.TCP, vip_target_rule=Port.rule4_ports, private_target_rule=Port.rule4_ports, vip_uuid=vip.get_vip().uuid)
        test.pf = zstack_pf_header.ZstackTestPortForwarding()
        test.pf.set_creation_option(pf_creation_opt)
        test.pf.create()
        vip.attach_pf(test.pf)
        vip.check()
        vpc_pf_check(vm2, vip, test.pf)
        
    test_lib.lib_error_cleanup(test_obj_dict)
    test_stub.remove_all_vpc_ha_group()
    test_stub.remove_all_vpc_vrouter()


def env_recover():
    with test_lib.ignored(AttributeError):
        test.pf.delete()
    test_lib.lib_error_cleanup(test_obj_dict)
    test_stub.remove_all_vpc_ha_group()
    test_stub.remove_all_vpc_vrouter()

