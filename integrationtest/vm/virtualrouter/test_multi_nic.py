'''
New Integration Test for Multi Nics.

@author: Glody
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.net_operations as net_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstacklib.utils.ssh as ssh
import os

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def test():
    test_util.test_dsc('Create vrouter vm and check if the second public nic attached to vrouter')
    vm1 = test_stub.create_vlan_vm(os.environ.get('l3VlanNetworkName1'))
    test_obj_dict.add_vm(vm1)
    vm1_ip = vm1.get_vm().vmNics[0].ip
    vr1 = test_lib.lib_find_vr_by_vm(vm1.vm)[0]
    vr1_uuid = vr1.uuid
    vr1_pub_ip = test_lib.lib_find_vr_pub_ip(vr1)
    vr1_private_ip = test_lib.lib_find_vr_private_ip(vr1)
    l3network1_uuid = vm1.get_vm().vmNics[0].l3NetworkUuid
    cond = res_ops.gen_query_conditions('uuid', '=', l3network1_uuid)
    l3network1_cidr = res_ops.query_resource(res_ops.L3_NETWORK, cond)[0].ipRanges[0].networkCidr

    cond = res_ops.gen_query_conditions('name', '=', 'l3_user_defined_vlan1')
    second_public_l3network_uuid = res_ops.query_resource(res_ops.L3_NETWORK, cond)[0].uuid
    net_ops.attach_l3(second_public_l3network_uuid, vr1_uuid) 

    #Attach second public network to vrouter   
    cond = res_ops.gen_query_conditions('uuid', '=', vr1_uuid)
    vr1_nics = res_ops.query_resource(res_ops.APPLIANCE_VM, cond)[0].vmNics
    second_public_l3network_attached = False
    for vm_nic in vr1_nics:
        if vm_nic.l3NetworkUuid == second_public_l3network_uuid:
            second_public_l3network_attached = True
    if not second_public_l3network_attached:
        net_ops.attach_l3(second_public_l3network_uuid, vr1_uuid)

    #Get vr1 nic_uuid on second public network
    vr1_nics = res_ops.query_resource(res_ops.APPLIANCE_VM, cond)[0].vmNics
    vr1_second_pub_nic_uuid = ''
    for vm_nic in vr1_nics:
        if vm_nic.l3NetworkUuid == second_public_l3network_uuid:
            vr1_second_pub_nic_uuid = vm_nic.uuid
            test_util.test_pass('The Second Public Nic Is Attached To Vrouter')
    if vr1_second_pub_nic_uuid != '':
        net_ops.detach_l3(vr1_second_pub_nic_uuid)
    vm1.check()
    vm1.destroy()
    test_util.test_fail('The Second Public Nic Does Not Attached To Vrouter')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
