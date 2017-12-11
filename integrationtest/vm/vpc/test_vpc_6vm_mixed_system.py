'''
@author: FangSun
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import os
from itertools import izip

VLAN1_NAME, VLAN2_NAME = ['l3VlanNetworkName1', "l3VlanNetwork2"]
VXLAN1_NAME, VXLAN2_NAME = ["l3VxlanNetwork11", "l3VxlanNetwork12"]

CLASSIC_L3 = 'l3NoVlanNetworkName2'
PUB_L3 = 'l3PublicNetworkName'

vpc1_l3_list = [VLAN1_NAME, VLAN2_NAME]
vpc2_l3_list = [VXLAN1_NAME, VXLAN2_NAME]

vpc_l3_list = [vpc1_l3_list, vpc2_l3_list]
all_l3_list = vpc1_l3_list + vpc2_l3_list + [CLASSIC_L3] + [PUB_L3]

vpc_name_list = ['vpc1','vpc2']

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
vr_list = []

BASIC='basic'
MIGRATE='migrate'
SNAPSHOT= 'snapshot'
VM_VOLUME = 'volume_attach'

case_flavor = dict(vm_ops=       dict(ops=BASIC),
                   vm_migrate=   dict(ops=MIGRATE),
                   vm_snapshot=  dict(ops=SNAPSHOT),
                   vm_volume  =  dict(ops=VM_VOLUME)
                   )


def test():
    flavor = case_flavor[os.environ.get('CASE_FLAVOR')]
    test_util.test_dsc("create vpc vrouter and attach vpc l3 to vpc")
    for vpc_name in vpc_name_list:
        vr_list.append(test_stub.create_vpc_vrouter(vpc_name))
    for vr, l3_list in izip(vr_list, vpc_l3_list):
        test_stub.attach_l3_to_vpc_vr(vr, l3_list)

    vm_list = []
    for l3_name in all_l3_list:
        vm = test_stub.create_vm_with_random_offering(vm_name='vpc_vm_{}'.format(l3_name), l3_name=l3_name)
        test_obj_dict.add_vm(vm)
        vm_list.append(vm)

    for vm in vm_list:
        vm.check()

    if flavor['ops'] is BASIC:
        for vm in vm_list:
            for action in ('stop', 'start', 'check', 'reboot', 'suspend', 'resume', 'check'):
                getattr(vm, action)()
    elif flavor['ops'] is MIGRATE:
        for vm in vm_list:
            test_stub.migrate_vm_to_random_host(vm)
            vm.check()
    elif flavor['ops'] is SNAPSHOT:
        for vm in vm_list:
            snapshots_list = []
            for volume in vm.get_vm().allVolumes:
                snapshots = test_obj_dict.get_volume_snapshot(volume.uuid)
                snapshots.set_utility_vm(vm)
                snapshots.create_snapshot('create_volume_snapshot')
                snapshots_list.append(snapshots)

            vm.stop()
            vm.check()

            for snapshots in snapshots_list:
                snapshot = snapshots.get_current_snapshot()
                snapshots.use_snapshot(snapshot)

            vm.start()
            vm.check()
    elif flavor['ops'] is VM_VOLUME:
        volume = test_stub.create_multi_volumes(count=1)[0]
        test_obj_dict.add_volume(volume)
        for vm in vm_list:
            volume.attach(vm)
            vm.check()
            volume.detach()
            vm.check()

    test_lib.lib_error_cleanup(test_obj_dict)
    test_stub.remove_all_vpc_vrouter()


def env_recover():
    test_lib.lib_error_cleanup(test_obj_dict)
    test_stub.remove_all_vpc_vrouter()
