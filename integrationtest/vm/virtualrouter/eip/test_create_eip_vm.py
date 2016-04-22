'''

Test create EIP for a VM. 

Test step:
    1. Create a VM
    2. Create a EIP with VM's nic
    3. Check the EIP connectibility
    4. Destroy VM

@author: Youyk
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import os

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def test():
    test_util.test_dsc('Create test vm with EIP and check.')
    vm = test_stub.create_vlan_vm(os.environ.get('l3VlanNetworkName1'))
    test_obj_dict.add_vm(vm)
    
    l3_name = os.environ.get('l3NoVlanNetworkName1')
    l3_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid

    l3_name = os.environ.get('l3VlanNetworkName1')
    pri_l3_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid

    vm_nic = vm.vm.vmNics[0]
    vm_nic_uuid = vm_nic.uuid
    vip = test_stub.create_vip('create_eip_test', l3_uuid)
    test_obj_dict.add_vip(vip)
    eip = test_stub.create_eip('create eip test', vip_uuid=vip.get_vip().uuid, vnic_uuid=vm_nic_uuid, vm_obj=vm)
    
    vip.attach_eip(eip)
    
    vm.check()
    vip.check()
    vm.destroy()
    test_obj_dict.rm_vm(vm)
    vip.check()
    eip.delete()
    vip.delete()
    test_obj_dict.rm_vip(vip)
    test_util.test_pass('Create EIP for VM Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)
