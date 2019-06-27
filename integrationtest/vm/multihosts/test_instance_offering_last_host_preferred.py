'''

New Integration Test for instance offering allocator strategy 'LastHostPreferredAllocatorStrategy'.

@author: chenyuan.xu
'''
import zstackwoodpecker.test_util as test_util
import os
import time
import apibinding.inventory as inventory
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.host_operations as host_ops
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.tag_operations as tag_ops
import zstackwoodpecker.operations.vm_operations as vm_ops
import zstackwoodpecker.operations.config_operations as config_ops

vm = None
test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def test():
    global vm
    config_ops.change_global_config('localStoragePrimaryStorage', 'liveMigrationWithStorage.allow', 'true')
    test_util.test_dsc('create instance offering')
    instance_offering_option = test_util.InstanceOfferingOption()
    instance_offering_option.set_cpuNum(1)
    instance_offering_option.set_memorySize(1*1024*1024*1024)
    instance_offering_option.set_allocatorStrategy("")
    instance_offering_option.set_type("UserVm")
    instance_offering_option.set_name('new_offering')
    instance_offering_option.set_allocatorStrategy("LastHostPreferredAllocatorStrategy")
    new_offering = vm_ops.create_instance_offering(instance_offering_option)
    test_obj_dict.add_instance_offering(new_offering)    
    image_name = os.environ.get('imageName_s')
    l3_name = os.environ.get('l3VlanNetworkName1')
    vm = test_stub.create_vm_with_instance_offering('test-vm',image_name,l3_name, new_offering)
    test_obj_dict.add_vm(vm)
#    vm.check()
    host_ip1 = test_lib.lib_find_host_by_vm(vm.get_vm()).managementIp
    vm.stop()
    vm.start() 
    host_ip2 = test_lib.lib_find_host_by_vm(vm.get_vm()).managementIp
    if host_ip1 != host_ip2:
        test_util.test_fail("Host ip changed after vm stopped and started")

    test_stub.migrate_vm_to_random_host(vm)
    host_ip1 = test_lib.lib_find_host_by_vm(vm.get_vm()).managementIp
    vm.stop()
    vm.start()
    host_ip2 = test_lib.lib_find_host_by_vm(vm.get_vm()).managementIp
    if host_ip1 != host_ip2:
        test_util.test_fail("Host ip changed after vm stopped and started")

    ps = test_lib.lib_get_primary_storage_by_uuid(vm.get_vm().allVolumes[0].primaryStorageUuid)
    host = test_lib.lib_find_host_by_vm(vm.get_vm())
    host_ops.change_host_state(host.uuid, "maintain")
    vm.stop()
    if ps.type == inventory.LOCAL_STORAGE_TYPE:    
        try:
            vm.start()
        except Exception as e:
            host_ops.change_host_state(host.uuid, "enable")
            test_stub.ensure_hosts_connected(180)
            vm.start()
    else:
        try:
            vm.start()
        except Exception as e:
            test_util.test_fail(e)

    host = test_lib.lib_find_host_by_vm(vm.get_vm())
    host_ops.change_host_state(host.uuid, "disable")
    vm.stop()
    if ps.type == inventory.LOCAL_STORAGE_TYPE:
        try:
            vm.start()
        except Exception as e:
            host_ops.change_host_state(host.uuid, "enable")
            test_stub.ensure_hosts_connected(180)
            vm.start()
    else:
        try:
            vm.start()
        except Exception as e:
            test_util.test_fail(e)
            host_ops.change_host_state(host.uuid, "enable")

    vm.stop()    
    host_management_ip = host.managementIp
    host_ops.update_host(host.uuid, 'managementIp', '222.222.222.222')
    try:
        host_ops.reconnect_host(host.uuid)
    except:
        cond = res_ops.gen_query_conditions('uuid', '=', host.uuid)
        bs_status = res_ops.query_resource(res_ops.HOST, cond)[0].status
    count = 0
    while count < 60:
        if host.status == "Disconnected":
            break
        time.sleep(5)
        count += 1
    if ps.type == inventory.LOCAL_STORAGE_TYPE:
        try:
            vm.start()
        except Exception as e:
            test_util.test_logger(e)
    else:
        try:
            vm.start()
        except Exception as e:
            test_util.test_fail(e)

    host_ops.update_host(host.uuid, 'managementIp', host_management_ip)
    host_ops.reconnect_host(host.uuid)
    vm.destroy()
    test_util.test_pass('Migrate VM Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)
