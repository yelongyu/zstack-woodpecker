'''
    Test Description:
        Will create 1 test VM with 1 NIC firstly. 
        Then will attach a new NIC to VM with different L3 Network.

@author: YYK
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import os

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def test():
    test_util.test_dsc('''
    Test Description:
        Will create 1 test VM with 1 NIC firstly. 
        Then will attach a new NIC to VM with different L3 Network.
    ''')
    image_name = os.environ.get('imageName_net')
    image_uuid = test_lib.lib_get_image_by_name(image_name).uuid
    #l3_name = os.environ.get('l3VlanNetworkName1')
    l3_name = os.environ.get('l3VlanDNATNetworkName')
    l3_net_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
    l3_net_list = [l3_net_uuid]
    l3_name = os.environ.get('l3VlanNetworkName1')
    l3_net_uuid2 = test_lib.lib_get_l3_by_name(l3_name).uuid

    vm = test_stub.create_vm(l3_net_list, image_uuid, 'attach_nic_vm', \
            default_l3_uuid = l3_net_uuid)
    test_obj_dict.add_vm(vm)
    vm.check()
    vm.add_nic(l3_net_uuid2)
    attached_nic = test_lib.lib_get_vm_last_nic(vm.get_vm())
    if l3_net_uuid2 != attached_nic.l3NetworkUuid:
        test_util.test_fail("After attach a nic, VM:%s last nic is not belong l3: %s" % (vm.get_vm().uuid, l3_net_uuid2))

    test_lib.lib_restart_vm_network(vm.get_vm())

    vm.check()

    vm.remove_nic(attached_nic.uuid)

    attached_nic = test_lib.lib_get_vm_last_nic(vm.get_vm())
    if l3_net_uuid != attached_nic.l3NetworkUuid:
        test_util.test_fail("After detached NIC, VM:%s only nic is not belong l3: %s" % (vm.get_vm().uuid, l3_net_uuid2))

    vm.destroy()
    test_util.test_pass('Test Attach Nic to VM successfully.')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)

