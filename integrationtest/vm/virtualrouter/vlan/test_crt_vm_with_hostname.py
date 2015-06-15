'''

@author: Youyk
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import os

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def test():
    test_util.test_dsc('Create test vm with hostname and check. VR has DNS SNAT EIP PF and DHCP services')
    l3_name = os.environ.get('l3VlanNetworkName1')
    vm_hostname = ('test_vm_hostname')
    hostname_tag = test_lib.lib_create_vm_hostname_tag(vm_hostname)
    vm = test_stub.create_vlan_vm(os.environ.get('l3VlanNetworkName1'), system_tags=hostname_tag)
    test_obj_dict.add_vm(vm)
    vm.check()
    #TODO: check vm's hostname

    vm.destroy()
    test_util.test_pass('Create VirtualRouter VM DNS DHCP SANT EIP PF Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
