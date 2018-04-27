'''
test for migrating vm with iscsi storage 
@author: guocan
'''

import apibinding.inventory as inventory
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.vm_operations as vm_ops
import zstackwoodpecker.operations.vcenter_operations as vct_ops
import test_stub
import os

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()


def test():
    global test_obj_dict

    #enable vmware vmotion
    SI = vct_ops.connect_vcenter(os.environ['vcenter'])
    content = SI.RetrieveContent()
    hosts = vct_ops.get_host(content)
    for host in hosts:
        vct_ops.enable_vmotion(host)

    network_pattern = 'L3-%s'%os.environ['dportgroup']
    if not vct_ops.lib_get_vcenter_l3_by_name(network_pattern):
        network_pattern = 'L3-%s'%os.environ['portgroup0']
    ova_image_name = os.environ['vcenterDefaultmplate']
    disk_offering = test_lib.lib_get_disk_offering_by_name(os.environ.get('largeDiskOfferingName'))

    #create vm 
    vm = test_stub.create_vm_in_vcenter(vm_name = 'migrate_vm', image_name = ova_image_name, l3_name = network_pattern)
    vm.check()
    test_obj_dict.add_vm(vm)
    #check whether vm migration candidate hosts exist
    candidate_hosts = vm_ops.get_vm_migration_candidate_hosts(vm.vm.uuid).inventories
    if candidate_hosts == []:
        test_util.test_logger('Not find vm migration candidate hosts, skip test migrate vm')
    else:
        test_util.test_dsc('Migrate vm from the current host')
        vm_ops.migrate_vm_for_vcenter(vm.vm.uuid, current_host_uuid = vm.vm.hostUuid)
        vm.update()
        vm.check()
        #check the consistency of the migration in zstack and vmware
        assert test_lib.lib_find_host_by_vm(vm.vm).name == vct_ops.find_host_by_vm(content, vm.vm.name)
        test_util.test_dsc('Migrate vm to the specified host')
        candidate_host = vm_ops.get_vm_migration_candidate_hosts(vm.vm.uuid).inventories[0]
        host_uuid = candidate_host.uuid
        vm_ops.migrate_vm_for_vcenter(vm.vm.uuid, host_uuid)
        vm.update()
        vm.check()
        #check whether the specified host is effective
        assert candidate_host.name == test_lib.lib_find_host_by_vm(vm.vm).name
        assert candidate_host.name == vct_ops.find_host_by_vm(content, vm.vm.name)
        test_util.test_dsc('vm in suspended state does not allow migration')
        vm.suspend()
        candidate_host = vm_ops.get_vm_migration_candidate_hosts(vm.vm.uuid).inventories
        assert candidate_host == []
        
    #create vm with disk
    vm1 = test_stub.create_vm_in_vcenter(vm_name = 'migrate_vm_with_disk', image_name = ova_image_name, l3_name = network_pattern, disk_offering_uuids = [disk_offering.uuid])
    vm1.check()
    test_obj_dict.add_vm(vm1)
    #check whether vm migration candidate hosts exist
    candidate_hosts = vm_ops.get_vm_migration_candidate_hosts(vm1.vm.uuid).inventories
    if candidate_hosts == []:
        test_util.test_logger('Not find vm migration candidate hosts, skip test migrate vm with disk')
    else:
        test_util.test_dsc('Migrate vm with disk from the current host')
        vm_ops.migrate_vm_for_vcenter(vm1.vm.uuid, current_host_uuid = vm1.vm.hostUuid)
        vm1.update()
        vm1.check()
        assert test_lib.lib_find_host_by_vm(vm1.vm).name == vct_ops.find_host_by_vm(content, vm1.vm.name)
        test_util.test_dsc('Migrate vm with disk to the specified host')
        candidate_host = vm_ops.get_vm_migration_candidate_hosts(vm1.vm.uuid).inventories[0]
        host_uuid = candidate_host.uuid
        vm_ops.migrate_vm_for_vcenter(vm1.vm.uuid, host_uuid)
        vm1.update()
        vm1.check()
        assert candidate_host.name == test_lib.lib_find_host_by_vm(vm1.vm).name
        assert candidate_host.name == vct_ops.find_host_by_vm(content, vm1.vm.name)
   
    #cleanup 
    test_lib.lib_error_cleanup(test_obj_dict)

    test_util.test_pass("Migrate vm test passed.")


def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)