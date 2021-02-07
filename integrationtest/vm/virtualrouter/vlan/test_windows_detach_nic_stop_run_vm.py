'''
    Test Description:
	This case is test for detach a NIC from a stop or a running windows VM 
        Will create 1 test windows VM with 1 NIC firstly. 
        Then attach a new NIC to Stopped VM with different L3 Network.
        Then Stop the VM.
        Then detach the new NIC
        Then start the VM and check the network.
        Then attach a new NIC again
        Then detach the NIC

@author: Pengtao.Zhang
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import time
import os

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def test():
    test_util.test_dsc('''
    Test Description:
        This case is test for detach a NIC from a stop or a running windows VM 
        Will create 1 test windows VM with 1 NIC firstly. 
        Then attach a new NIC to Stopped VM with different L3 Network.
        Then Stop the VM.
        Then detach the new NIC
        Then start the VM and check the network.
        Then attach a new NIC again
        Then detach the NIC
    ''')
    image_name = os.environ.get('imageName_windows')
    image_uuid = test_lib.lib_get_image_by_name(image_name).uuid
    l3_name = os.environ.get('l3VlanNetworkName1')
    l3_net_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
    l3_net_list = [l3_net_uuid]
    l3_name2 = os.environ.get('l3VlanNetworkName5')
    l3_net_uuid2 = test_lib.lib_get_l3_by_name(l3_name2).uuid
    vm_instance_offering = test_lib.lib_create_instance_offering(cpuNum = 2,
                                                                memorySize = 2048 * 1024 * 1024)
    test_obj_dict.add_instance_offering(vm_instance_offering)

    vm = test_stub.create_vm(l3_net_list, image_uuid, 'windows2012_vm', \
            default_l3_uuid = l3_net_uuid, instance_offering_uuid = vm_instance_offering.uuid)
    test_obj_dict.add_vm(vm)

    vm.add_nic(l3_net_uuid2)
    attached_nic = test_lib.lib_get_vm_last_nic(vm.get_vm())
    if l3_net_uuid2 != attached_nic.l3NetworkUuid:
        test_util.test_fail("After attach a nic, VM:%s last nic is not belong l3: %s" % (vm.get_vm().uuid, l3_net_uuid2))

    vm.stop()
    time.sleep(5)
    
    vm.remove_nic(attached_nic.uuid)
    time.sleep(5)

    vm.start()
    time.sleep(50)

    vm.add_nic(l3_net_uuid2)
    attached_nic = test_lib.lib_get_vm_last_nic(vm.get_vm())
    if l3_net_uuid2 != attached_nic.l3NetworkUuid:
        test_util.test_fail("After attach a nic again, VM:%s last nic is not belong l3: %s" % (vm.get_vm().uuid, l3_net_uuid2))
    
    time.sleep(5)
    vm.remove_nic(attached_nic.uuid)
    time.sleep(5)

    vm.destroy()
    test_util.test_pass('Test Attach Nic with VM reboot action successfully.')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)

