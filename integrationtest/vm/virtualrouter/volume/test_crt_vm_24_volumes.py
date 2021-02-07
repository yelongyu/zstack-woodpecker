'''

Create a VM with vlan L3 network and 22 data volume offering.

@author: Youyk
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import os

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def test():
    global test_obj_dict
    test_util.test_dsc('Create test vm and check. VR only has DNS and DHCP services')
    vm = test_stub.create_vlan_vm_with_volume(os.environ.get('l3VlanNetworkName1'), None, 22)
    test_obj_dict.add_vm(vm)
    vm.check()
    volumes_number = len(test_lib.lib_get_all_volumes(vm.vm))
    if volumes_number != 23:
        test_util.test_fail('Did not find 23 volumes for [vm:] %s. But we assigned 22 data volume when create the vm. We only catch %s volumes' % (vm.vm.uuid, volumes_number))
    else:
        test_util.test_logger('Find 22 volumes for [vm:] %s.' % vm.vm.uuid)

    vm.destroy()
    test_util.test_pass('Create VirtualRouter VM DNS DHCP Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)
