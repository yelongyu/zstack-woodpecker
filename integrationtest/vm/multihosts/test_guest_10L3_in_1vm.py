'''

@author: Youyk
'''
from zstackwoodpecker import test_util
from zstackwoodpecker import teststate
import zstackwoodpecker.operations.resource_operations as resource_operations
import zstackwoodpecker.operations.account_operations as account_operations

test_stub = test_lib.lib_get_test_stub()
vm = None

def test():
    '''
    Test Description:
        Will create 1 VM with 10 VR l3 networks. 
    Resource required:
        Need support 11 VMs (1 test VM + 10 VR VMs) existing at the same time. 
    '''
    global vm
    l3net_uuids = []
    for i in range(10):
        i += 1
        l3net_uuid = resource_operations.get_resource(resource_operations.L3_NETWORK, session_uuid=None, name=(("guestL3VlanNetwork") + str(i)))[0].uuid
        l3net_uuids.append(l3net_uuid)
    vm_create_option = test_util.VmOption()
    vm_create_option.l3_uuids = l3net_uuids
    vm = test_stub.lib_create_vm(vm_create_option)
    test_stub.lib_check_vm_status(vm)
    test_util.test_logger('VM network config checking pass')
    test_stub.lib_destroy_vm(vm)
    test_util.test_pass('Create 1 VM with 10 vlan VR l3_network successfully.')

#Will be called only if exception happens in test().
def error_cleanup():
    global vm
    if vm:
        test_stub.lib_destroy_vm(vm)
