'''

Create a VM with 4 additional data volumes with 28 of them using virtio-scsi

@author: Quarkonics
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import os

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def test():
    global test_obj_dict
    test_util.test_dsc('Create a VM with 3 additional data volumes with 1 of them using virtio-scsi')
    disk_offering1 = test_lib.lib_get_disk_offering_by_name(os.environ.get('smallDiskOfferingName'))
    disk_offering_uuids = []
    for i in range(0, 8):
        disk_offering_uuids.append(disk_offering1.uuid)
    disk_offering2 = test_lib.lib_get_disk_offering_by_name(os.environ.get('rootDiskOfferingName'))
    for i in range(0, 14):
        disk_offering_uuids.append(disk_offering2.uuid)
    vm = test_stub.create_vlan_vm(system_tags=["virtio::diskOffering::%s::num::14" % (disk_offering2.uuid) ,"virtio::diskOffering::%s::num::14" % (disk_offering1.uuid)], l3_name=os.environ.get('l3VlanNetworkName1'), disk_offering_uuids=disk_offering_uuids)
    test_obj_dict.add_vm(vm)
    vm.check()
    volumes_number = len(test_lib.lib_get_all_volumes(vm.vm))
    if volumes_number != 23:
        test_util.test_fail('Did not find 23 volumes for [vm:] %s. But we assigned 22 data volume when create the vm. We only catch %s volumes' % (vm.vm.uuid, volumes_number))
    else:
        test_util.test_logger('Find 23 volumes for [vm:] %s.' % vm.vm.uuid)

    scsi_cmd = 'ls /dev/sd* | wc -l'
    if test_lib.lib_execute_command_in_vm(vm.get_vm(), scsi_cmd).strip() != '22':
        test_util.test_fail('Only expect 22 disk in virtio scsi mode')

    vm.destroy()
    test_util.test_pass('Create a VM with 22 additional data volumes with 22 of them using virtio-scsi PASS')

#Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)
