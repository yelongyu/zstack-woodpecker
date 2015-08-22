'''
Change static IP address
@author: Youyk
'''
import os
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.net_operations as net_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.tag_operations as tag_ops

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def test():
    test_util.test_dsc('Create test vm with static ip address and check. VR has DNS SNAT EIP PF and DHCP services')
    l3_name = os.environ.get('l3VlanNetworkName1')
    l3_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
    ip_address = net_ops.get_free_ip(l3_uuid)[0].ip
    static_ip_system_tag = test_lib.lib_create_vm_static_ip_tag(l3_uuid, \
            ip_address)
    vm = test_stub.create_vlan_vm(os.environ.get('l3VlanNetworkName1'), system_tags=[static_ip_system_tag])
    test_obj_dict.add_vm(vm)
    vm.stop()
    
    cond = res_ops.gen_query_conditions('tag', '=', static_ip_system_tag)
    system_tag = res_ops.query_resource(res_ops.SYSTEM_TAG, cond)[0]

    ip_address2 = net_ops.get_free_ip(l3_uuid)[0].ip
    static_ip_system_tag2 = test_lib.lib_create_vm_static_ip_tag(l3_uuid, \
            ip_address2)
    tag_ops.update_system_tag(system_tag.uuid, static_ip_system_tag2)

    vm.start()
    if ip_address2 != vm.get_vm().vmNics[0].ip:
        test_util.test_fail('VM static ip test failed')
    vm.check()
    vm.destroy()
    test_util.test_pass('Create VM with static IP and change static IP Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
