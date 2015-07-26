'''

@author: Youyk
'''
import os
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.net_operations as net_ops

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def test():
    test_util.test_dsc('Create test vm with static ip address and check. VR has DNS SNAT EIP PF and DHCP services')
    l3_name = os.environ.get('l3VlanNetworkName1')
    l3_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
    ip_address = net_ops.get_free_ip(l3_uuid)[0].ip
    static_ip_system_tag = test_lib.lib_create_vm_static_ip_tag(l3_uuid, ip_address)
    vm = test_stub.create_vlan_vm(os.environ.get('l3VlanNetworkName1'), system_tags=static_ip_system_tag)
    test_obj_dict.add_vm(vm)
    vm.check()
    if ip_address != vm.get_vm().vmNics[0].ip:
        test_util.test_fail('VM static ip test failed')

    vm.destroy()
    test_util.test_pass('Create VirtualRouter VM DNS DHCP SANT EIP PF Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
