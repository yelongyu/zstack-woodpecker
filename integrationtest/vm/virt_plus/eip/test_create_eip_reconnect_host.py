'''
Test create eip and reconnect host
@author: SyZhao
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.host_operations as host_ops
import os

test_stub = test_lib.lib_get_specific_stub()
test_obj_dict = test_state.TestStateDict()

def test():
    test_util.test_dsc('Create test vm with EIP and check.')
    vm = test_stub.create_vlan_vm(os.environ.get('l3VlanNetworkName1'))
    test_obj_dict.add_vm(vm)

    host = test_lib.lib_get_vm_host(vm.get_vm())
    host_uuid = host.uuid

    pri_l3_name = os.environ.get('l3VlanNetworkName1')
    pri_l3_uuid = test_lib.lib_get_l3_by_name(pri_l3_name).uuid

    pub_l3_name = os.environ.get('l3PublicNetworkName')
    pub_l3_uuid = test_lib.lib_get_l3_by_name(pub_l3_name).uuid

    vm_nic = vm.vm.vmNics[0]
    vm_nic_uuid = vm_nic.uuid
    vip = test_stub.create_vip('create_eip_test', pub_l3_uuid)
    test_obj_dict.add_vip(vip)
    eip = test_stub.create_eip('create eip test', vip_uuid=vip.get_vip().uuid, vnic_uuid=vm_nic_uuid, vm_obj=vm)

    vip.attach_eip(eip)

    vm.check()

    host_ops.reconnect_host(host_uuid)

    if not test_lib.lib_check_directly_ping(vip.get_vip().ip):
        test_util.test_fail('expected to be able to ping vip while it fail')

    vm.destroy()

    test_obj_dict.rm_vm(vm)
    if test_lib.lib_check_directly_ping(vip.get_vip().ip):
        test_util.test_fail('not expected to be able to ping vip while it succeed')

    eip.delete()
    vip.delete()

    test_obj_dict.rm_vip(vip)
    test_util.test_pass('Create EIP for VM Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)

