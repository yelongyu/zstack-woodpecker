'''

Test EIP with vm operations. Create 2 VMs. 1 VM stopped. 2nd VM is attached a
EIP. Then start VM1 to check if everything is okay. This case is from a bug. 

@author: Youyk
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.net_operations as net_ops
import zstackwoodpecker.zstack_test.zstack_test_sg_vm as zstack_sg_vm_header
import apibinding.inventory as inventory

import os

Port = test_state.Port
test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def test():
    vm1 = test_stub.create_dnat_vm()
    test_obj_dict.add_vm(vm1)

    vm2 = test_stub.create_dnat_vm()
    test_obj_dict.add_vm(vm2)

    l3_name = os.environ.get('l3VlanNetworkName1')
    vr1_l3_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
    vrs = test_lib.lib_find_vr_by_l3_uuid(vr1_l3_uuid)
    temp_vm1 = None
    if not vrs:
        #create temp_vm1 for getting vlan1's vr for test vm portforwarding
        temp_vm1 = test_stub.create_vlan_vm()
        test_obj_dict.add_vm(temp_vm1)
        vr1 = test_lib.lib_find_vr_by_vm(temp_vm1.vm)[0]
    else:
        vr1 = vrs[0]

    l3_name = os.environ.get('l3NoVlanNetworkName1')
    vr2_l3_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
    vrs = test_lib.lib_find_vr_by_l3_uuid(vr2_l3_uuid)
    temp_vm2 = None
    if not vrs:
        #create temp_vm2 for getting novlan's vr for test pf_vm portforwarding
        temp_vm2 = test_stub.create_user_vlan_vm()
        test_obj_dict.add_vm(temp_vm2)
        vr2 = test_lib.lib_find_vr_by_vm(temp_vm2.vm)[0]
    else:
        vr2 = vrs[0]

    if temp_vm1:
        temp_vm1.destroy()
        test_obj_dict.rm_vm(temp_vm1)
    if temp_vm2:
        temp_vm2.destroy()
        test_obj_dict.rm_vm(temp_vm2)
    
    #stop vm
    vm1.stop()

    vm1_nic = vm1.vm.vmNics[0]
    vm1_nic_uuid = vm1_nic.uuid
    vm2_nic = vm2.vm.vmNics[0]
    vm2_nic_uuid = vm2_nic.uuid
    pri_l3_uuid = vm2_nic.l3NetworkUuid
    vr = test_lib.lib_find_vr_by_l3_uuid(pri_l3_uuid)[0]
    vr_pub_nic = test_lib.lib_find_vr_pub_nic(vr)
    l3_uuid = vr_pub_nic.l3NetworkUuid
    vip = test_stub.create_vip('vm_ops', l3_uuid)
    test_obj_dict.add_vip(vip)
    vip_uuid = vip.get_vip().uuid
    vip2 = test_stub.create_vip('vm_ops2', l3_uuid)
    test_obj_dict.add_vip(vip2)
    vip2_uuid = vip2.get_vip().uuid

    eip = test_stub.create_eip('eip vm ops test', vip_uuid, vm2_nic_uuid, vm2)
    vip.attach_eip(eip)

    test_util.test_dsc("start vm1")
    vm1.start()
    #vip.check()
    eip2 = test_stub.create_eip('eip vm ops test2', vip2_uuid, vm1_nic_uuid, vm1)
    vip2.attach_eip(eip2)

    vm1.destroy()
    test_obj_dict.rm_vm(vm1)
    vm2.destroy()
    test_obj_dict.rm_vm(vm2)

    vip.delete()
    test_obj_dict.rm_vip(vip)
    test_util.test_pass("Test EIP with VM ops2 Successfully")

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
