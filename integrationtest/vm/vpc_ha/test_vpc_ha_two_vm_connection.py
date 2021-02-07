'''
@author: yixin.wang
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


VLAN1_NAME, VLAN2_NAME = ['l3VlanNetworkName1', "l3VlanNetwork2"]
VXLAN1_NAME, VXLAN2_NAME = ["l3VxlanNetwork11", "l3VxlanNetwork12"]
VLAN3_NAME, VXLAN3_NAME = ["l3VlanNetwork5", "l3VxlanNetwork15"]
VLAN4_NAME, VXLAN4_NAME = ["l3VlanNetwork6", "l3VxlanNetwork16"]

vpc3_l3_list = [VLAN3_NAME, VXLAN3_NAME, VLAN4_NAME, VXLAN4_NAME]

vpc_ha_group_name_list = ['test_vpc_ha', 'test_vpc_ha_upgrade']
ha_group_vpc_name_list = ['vpc-test','vpc-test-peer']
ha_monitor_ip = ['192.168.0.1']


VM_REBOOT='vm_reboot'
VM_MIGRATE= 'vm_migrate'
VR_MIGRATE= 'vr_migrate'
VR_REBOOT = 'vr_reboot'
VR_RECONNECT = 'vr_reconnect'
HOST_RECONNECT = 'host_reconnect'


case_flavor = dict(vm1_vm2_one_l3_vlan=                    dict(vm1l3=VLAN1_NAME, vm2l3=VLAN1_NAME, ops=None, upgrade=True),
                   vm1_vm2_one_l3_vxlan=                   dict(vm1l3=VXLAN1_NAME, vm2l3=VXLAN1_NAME, ops=None, upgrade=True),
                   vm1_l3_vlan_vm2_l3_vlan=                dict(vm1l3=VLAN1_NAME, vm2l3=VLAN2_NAME, ops=None, upgrade=True),
                   vm1_l3_vxlan_vm2_l3_vxlan=              dict(vm1l3=VXLAN1_NAME, vm2l3=VXLAN2_NAME, ops=None, upgrade=True),
                   vm1_l3_vlan_vm2_l3_vxlan=               dict(vm1l3=VLAN1_NAME, vm2l3=VXLAN1_NAME, ops=None, upgrade=True),
                   vm1_vm2_one_l3_vlan_migrate=            dict(vm1l3=VLAN1_NAME, vm2l3=VLAN1_NAME, ops=VM_MIGRATE, upgrade=True),
                   vm1_l3_vlan_vm2_l3_vlan_migrate=        dict(vm1l3=VLAN1_NAME, vm2l3=VLAN2_NAME, ops=VM_MIGRATE, upgrade=True),
                   vm1_l3_vxlan_vm2_l3_vxlan_vrreboot=     dict(vm1l3=VXLAN1_NAME, vm2l3=VXLAN2_NAME, ops=VR_REBOOT, upgrade=True),
                   vm1_l3_vxlan_vm2_l3_vxlan_vmreboot=     dict(vm1l3=VXLAN1_NAME, vm2l3=VXLAN2_NAME, ops=VM_REBOOT, upgrade=True),
                   vm1_l3_vlan_vm2_l3_vlan_vrreconnect=    dict(vm1l3=VLAN1_NAME, vm2l3=VLAN2_NAME, ops=VR_RECONNECT, upgrade=True),
                   vm1_l3_vlan_vm2_l3_vlan_vr_migrate=     dict(vm1l3=VLAN1_NAME, vm2l3=VLAN2_NAME, ops=VR_MIGRATE, upgrade=True),
                   vm1_l3_vlan_vm2_l3_vxlan_hostreconnect= dict(vm1l3=VLAN1_NAME, vm2l3=VXLAN1_NAME, ops=HOST_RECONNECT, upgrade=True),
                   vm1_ha_vlan_vm2_ha_one_l3_vlan=         dict(vm1l3=VLAN3_NAME, vm2l3=VLAN3_NAME, ops=None, upgrade=False),
                   vm1_ha_vlan_vm2_ha_one_l3_vxlan=        dict(vm1l3=VXLAN3_NAME, vm2l3=VXLAN3_NAME, ops=None, upgrade=False),
                   vm1_ha_vlan_vm2_ha_vlan=                dict(vm1l3=VLAN3_NAME, vm2l3=VLAN4_NAME, ops=None, upgrade=False),
                   vm1_ha_vxlan_vm2_ha_vxlan=              dict(vm1l3=VXLAN3_NAME, vm2l3=VXLAN4_NAME, ops=None, upgrade=False),
                   vm1_ha_vlan_vm2_ha_vxlan=               dict(vm1l3=VLAN3_NAME, vm2l3=VXLAN4_NAME, ops=None, upgrade=False),
                   vm1_ha_vlan_vm2_ha_one_l3_vlan_migrate= dict(vm1l3=VLAN3_NAME, vm2l3=VLAN3_NAME, ops=VM_MIGRATE, upgrade=False),
                   vm1_ha_vlan_vm2_ha_vlan_migrate=        dict(vm1l3=VLAN3_NAME, vm2l3=VLAN4_NAME, ops=VM_MIGRATE, upgrade=False),
                   vm1_ha_vxlan_vm2_ha_vxlan_vrreboot=     dict(vm1l3=VXLAN3_NAME, vm2l3=VXLAN4_NAME, ops=VR_REBOOT, upgrade=False),
                   vm1_ha_vxlan_vm2_ha_vxlan_vmreboot=     dict(vm1l3=VXLAN3_NAME, vm2l3=VXLAN4_NAME, ops=VM_REBOOT, upgrade=False),
                   vm1_ha_vlan_vm2_ha_vlan_vrreconnect=    dict(vm1l3=VLAN3_NAME, vm2l3=VLAN4_NAME, ops=VR_RECONNECT, upgrade=False),
                   vm1_ha_vlan_vm2_ha_vlan_vr_migrate=     dict(vm1l3=VLAN3_NAME, vm2l3=VLAN4_NAME, ops=VR_MIGRATE, upgrade=False),
                   vm1_ha_vlan_vm2_ha_vxlan_hostreconnect= dict(vm1l3=VLAN3_NAME, vm2l3=VXLAN4_NAME, ops=HOST_RECONNECT, upgrade=False),
                   )


test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
ha_group_list = []
ha_vr_list = []

def upgrade_noha_vpc(vr, hagroupUuid):
    test_util.test_dsc("upgrade test_vpc to ha vpc")
    vr.stop()
    vr.start_with_tags(tags='haUuid::{}'.format(hagroupUuid))
    ha_vr_list.append(vr)
    ha_vr_list.append(test_stub.create_vpc_vrouter_with_tags(vr_name='{}-peer'.format(vr.inv.name), tags='haUuid::{}'.format(hagroupUuid)))

def test_two_vm_connectivity(vm_1, vm_2):
    for vm in (vm_1, vm_2):
            vm.check()
    test_util.test_dsc("test two vm connectivity")
    [test_stub.run_command_in_vm(vm.get_vm(), 'iptables -F') for vm in (vm_1,vm_2)]
    test_stub.check_icmp_between_vms(vm_1, vm_2, expected_result='PASS')
    test_stub.check_tcp_between_vms(vm_1, vm_2, ["22"], [])

def test():
    flavor = case_flavor[os.environ.get('CASE_FLAVOR')]    
    test_util.test_dsc("create vpc ha group and vrouter then attach vpc l3 to vpc")
    for ha_group_name in vpc_ha_group_name_list:
        ha_group_list.append(test_stub.create_vpc_ha_group(ha_group_name, ha_monitor_ip))
    
    for ha_vpc_name in ha_group_vpc_name_list:
        ha_vr_list.append(test_stub.create_vpc_vrouter_with_tags(ha_vpc_name, tags='haUuid::{}'.format(ha_group_list[0].uuid)))
    time.sleep(10)
    test_stub.add_dns_to_ha_vpc(ha_vr_list[0].inv.uuid)
    test_stub.attach_l3_to_vpc_vr(ha_vr_list[0], vpc3_l3_list)
    
    if flavor['upgrade']:
        vr = test_stub.create_vpc_vrouter()
        test_stub.attach_l3_to_vpc_vr(vr)

    test_util.test_dsc("create two vm, vm1 in l3 {}, vm2 in l3 {}".format(flavor['vm1l3'], flavor['vm2l3']))
    vm1, vm2 = [test_stub.create_vm_with_random_offering(vm_name='vpc_vm_{}'.format(name), l3_name=name) for name in (flavor['vm1l3'], flavor['vm2l3'])]

    [test_obj_dict.add_vm(vm) for vm in (vm1,vm2)]
    [vm.check() for vm in (vm1,vm2)]

    if flavor['upgrade']:
        if flavor['ops'] is VM_MIGRATE:
          test_stub.migrate_vm_to_random_host(vm2)
          test_two_vm_connectivity(vm1, vm2)
          upgrade_noha_vpc(vr, ha_group_list[1].uuid)
        elif flavor['ops'] is VM_REBOOT:
          vm1.reboot()
          test_two_vm_connectivity(vm1, vm2)
          upgrade_noha_vpc(vr, ha_group_list[1].uuid)
        elif flavor['ops'] is VR_REBOOT:
          vr.reboot()
          time.sleep(10)
          test_two_vm_connectivity(vm1, vm2)
          upgrade_noha_vpc(vr, ha_group_list[1].uuid)
        elif flavor['ops'] is VR_RECONNECT:
          vr.reconnect()
          test_two_vm_connectivity(vm1, vm2)
          upgrade_noha_vpc(vr, ha_group_list[1].uuid)
        elif flavor['ops'] is VR_MIGRATE:
          vr.migrate_to_random_host()
          test_two_vm_connectivity(vm1, vm2)
          upgrade_noha_vpc(vr, ha_group_list[1].uuid)
        elif flavor['ops'] is HOST_RECONNECT:
          host = test_lib.lib_find_host_by_vm(random.choice([vm1,vm2]).get_vm())
          host_ops.reconnect_host(host.uuid)
          test_two_vm_connectivity(vm1, vm2)
          upgrade_noha_vpc(vr, ha_group_list[1].uuid)
        elif flavor['ops'] is None:
          upgrade_noha_vpc(vr, ha_group_list[1].uuid)
          test_stub.update_ha_status(ha_group_list[1].uuid)
          test_stub.check_ha_status(ha_group_list[1].uuid)
    else:
        test_two_vm_connectivity(vm1, vm2)
        test_stub.update_ha_status(ha_group_list[0].uuid)
        test_stub.check_ha_status(ha_group_list[0].uuid)
        ha_group = res_ops.get_resource(res_ops.VPC_HA_GROUP, uuid=ha_group_list[0].uuid)
        vr_refs = ha_group[0].vrRefs
        for i in range(0,2):
          vr_uuid = vr_refs[i].uuid
          vr_inv = res_ops.get_resource(res_ops.APPLIANCE_VM, uuid=vr_uuid)
          ha_status = vr_inv[0].haStatus
          if ha_status=='Master':
              vr_ha = test_stub.ZstackTestVR(vr_inv[0])
              break

        if flavor['ops'] is VM_MIGRATE:
          test_stub.migrate_vm_to_random_host(vm2)
          test_stub.update_ha_status(ha_group_list[0].uuid)
          test_stub.check_ha_status(ha_group_list[0].uuid)
        elif flavor['ops'] is VM_REBOOT:
          vm1.reboot()
          test_stub.update_ha_status(ha_group_list[0].uuid)
          test_stub.check_ha_status(ha_group_list[0].uuid)
        elif flavor['ops'] is VR_REBOOT:
          vr_ha.reboot()
          test_stub.update_ha_status(ha_group_list[0].uuid)
          test_stub.check_ha_status(ha_group_list[0].uuid)
        elif flavor['ops'] is VR_RECONNECT:
          vr_ha.reconnect()
          test_stub.update_ha_status(ha_group_list[0].uuid)
          test_stub.check_ha_status(ha_group_list[0].uuid)
        elif flavor['ops'] is VR_MIGRATE:
          vr_ha.migrate_to_random_host()
          test_stub.update_ha_status(ha_group_list[0].uuid)
          test_stub.check_ha_status(ha_group_list[0].uuid)
        elif flavor['ops'] is HOST_RECONNECT:
          host = test_lib.lib_find_host_by_vm(random.choice([vm1,vm2]).get_vm())
          host_ops.reconnect_host(host.uuid)
          test_stub.update_ha_status(ha_group_list[0].uuid)
          test_stub.check_ha_status(ha_group_list[0].uuid)

    if flavor['ops'] is not None:
        for vm in (vm1, vm2):
            vm.check()

    test_two_vm_connectivity(vm1, vm2)
    test_lib.lib_error_cleanup(test_obj_dict)
    test_stub.remove_all_vpc_ha_group()
    test_stub.remove_all_vpc_vrouter()


def env_recover():
    test_lib.lib_error_cleanup(test_obj_dict)
    test_stub.remove_all_vpc_ha_group()
    test_stub.remove_all_vpc_vrouter()
