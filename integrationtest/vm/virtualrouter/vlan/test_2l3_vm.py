'''
    Test Description:
        Will create 1 test VM with 2 different vlan supported L3 network 
        virtual router service. 

        The 2nd L3 Network will the default L3 network.

    Resource required:
        Need support 2 VMs existing at the same time. 

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
        Will create 1 test VM with 2 different vlan supported L3 network virtual router service. 
    Resource required:
        Need support 2 VMs existing at the same time. 
    ''')
    image_name = os.environ.get('imageName_net')
    image_uuid = test_lib.lib_get_image_by_name(image_name).uuid
    #l3_name = os.environ.get('l3VlanNetworkName1')
    l3_name = os.environ.get('l3VlanDNATNetworkName')
    l3_net_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
    l3_net_list = [l3_net_uuid]
    l3_name = os.environ.get('l3VlanNetworkName1')
    l3_net_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
    l3_net_list.append(l3_net_uuid)

    vm = test_stub.create_vm(l3_net_list, image_uuid, '2_vlan_vm', \
            default_l3_uuid = l3_net_uuid)
    test_obj_dict.add_vm(vm)
    vm.check()

    vm.destroy()
    test_util.test_pass('Create 1 VM with 2 vlan l3_network successfully.')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)

