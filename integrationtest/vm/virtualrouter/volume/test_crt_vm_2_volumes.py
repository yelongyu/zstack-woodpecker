'''

Create a VM with 2 additional data volumes 

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
    disk_offering = test_lib.lib_get_disk_offering_by_name(os.environ.get('smallDiskOfferingName'))
    disk_offering_uuids = [disk_offering.uuid]
    disk_offering = test_lib.lib_get_disk_offering_by_name(os.environ.get('rootDiskOfferingName'))
    disk_offering_uuids.append(disk_offering.uuid)
    vm = test_stub.create_vlan_vm_with_volume(os.environ.get('l3VlanNetworkName1'), disk_offering_uuids)
    test_obj_dict.add_vm(vm)
    vm.check()
    volumes_number = len(test_lib.lib_get_all_volumes(vm.vm))
    if volumes_number != 3:
        test_util.test_fail('Did not find 3 volumes for [vm:] %s. But we assigned 2 data volume when create the vm. We only catch %s volumes' % (vm.vm.uuid, volumes_number))
    else:
        test_util.test_logger('Find 3 volumes for [vm:] %s.' % vm.vm.uuid)

    vm.destroy()
    test_util.test_pass('Create VirtualRouter VM DNS DHCP Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)
