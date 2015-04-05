'''

Test Delete VIP before Attach its EIP to any VM

Test step:
    1. Create a VM
    2. Create an EIP without any VM.
    3. Check the EIP connectibility
    4. Check EIP
    5. Destroy VM

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
    vm.check()

    vm_nic = vm.vm.vmNics[0]
    vm_nic_uuid = vm_nic.uuid
    pri_l3_uuid = vm_nic.l3NetworkUuid
    vr = test_lib.lib_find_vr_by_l3_uuid(pri_l3_uuid)[0]
    vr_pub_nic = test_lib.lib_find_vr_pub_nic(vr)
    l3_uuid = vr_pub_nic.l3NetworkUuid
    vip = test_stub.create_vip('delete_vip_before_attach_eip_test', l3_uuid)
    test_obj_dict.add_vip(vip)

    eip = test_stub.create_eip('create eip test', vip_uuid=vip.get_vip().uuid)
    vip.attach_eip(eip)
    vip.check()

    vip.delete()
    test_obj_dict.rm_vip(vip)
    vm.destroy()
    test_obj_dict.rm_vm(vm)
    test_util.test_pass('Delete VIP before Attach EIP to Any VM Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)
