'''
    Test Description:
        Will create 1 VM with 3 l3 networks. 1 l3_network is not using VR; 1 l3_network is using novlan VR; 1 l3_network is using vlan VR. 
    Resource required:
        Need support 3 VMs (1 test VM + 2 VR VMs) existing at the same time. 
        This test required a special image, which was configed with at least 3 enabled NICs (e.g. eth0, eth1, eth2).


@author: Youyk
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
        Will create 1 VM with 3 l3 networks. 1 l3_network is not using VR; 1 l3_network is using novlan VR; 1 l3_network is using vlan VR. 
    Resource required:
        Need support 3 VMs (1 test VM + 2 VR VMs) existing at the same time. 
        This test required a special image, which was configed with at least 3 enabled NICs (e.g. eth0, eth1, eth2).
    ''')
    image_name = os.environ.get('imageName_net')
    image_uuid = test_lib.lib_get_image_by_name(image_name).uuid
    l3_name = os.environ.get('l3VlanNetworkName1')
    l3_net_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
    l3_net_list = [l3_net_uuid]
    l3_name = os.environ.get('l3VlanNetworkName3')
    l3_net_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
    l3_net_list.append(l3_net_uuid)
    l3_name = os.environ.get('l3PublicNetworkName')
    l3_net_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
    l3_net_list.append(l3_net_uuid)

    vm = test_stub.create_vm(l3_net_list, image_uuid, '3_l3_vm')
    test_obj_dict.add_vm(vm)
    vm.check()

    if len(vm.vm.vmNics) == 3:
        test_util.test_logger("Find 3 expected Nics in new created VM.")
    else:
        test_util.test_fail("New create VM doesn't not have 3 Nics. It only have %s" % len(vm.get_vm().vmNics))

    vm.destroy()
    test_util.test_pass('Create 1 VM with 3 l3_network (1 vlan VR, 1 novlan VR and 1 no VR L3network) successfully.')

#Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)
