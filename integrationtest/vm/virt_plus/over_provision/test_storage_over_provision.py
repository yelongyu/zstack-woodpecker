'''
This case can not execute parallelly
@author: Youyk
'''
import os
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.host_operations as host_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.vm_operations as vm_ops
import zstackwoodpecker.operations.volume_operations as vol_ops

_config_ = {
        'timeout' : 1000,
        'noparallel' : True
        }

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
original_rate = None
new_offering_uuid = None

def test():
    global original_rate
    global new_offering_uuid
    test_util.test_dsc('Test storage over provision method')
    zone_uuid = res_ops.query_resource(res_ops.ZONE)[0].uuid
    cond = res_ops.gen_query_conditions('state', '=', 'Enabled')
    cond = res_ops.gen_query_conditions('status', '=', 'Connected', cond)
    host = res_ops.query_resource_with_num(res_ops.HOST, cond, limit = 1)
    if not host:
        test_util.test_skip('No Enabled/Connected host was found, skip test.' )
        return True

    host = host[0]
    over_provision_rate = 2.5
    target_volume_num = 12
    kept_disk_size = 10 * 1024 * 1024

    vm = test_stub.create_vm(vm_name = 'storage_over_prs_vm_1')
    test_obj_dict.add_vm(vm)

    host_res = test_lib.lib_get_cpu_memory_capacity(host_uuids = [host.uuid])
    ps_res = test_lib.lib_get_storage_capacity(zone_uuids = [zone_uuid])
    avail_cap = ps_res.availableCapacity
    if avail_cap < kept_disk_size:
        test_util.test_skip('available disk capacity:%d is too small, skip test.' % avail_cap)
        return True

    original_rate = test_lib.lib_set_provision_storage_rate(over_provision_rate)
    data_volume_size = int(over_provision_rate * (avail_cap - kept_disk_size) / target_volume_num)
    disk_offering_option = test_util.DiskOfferingOption()
    disk_offering_option.set_name('storage-over-ps-test')
    disk_offering_option.set_diskSize(data_volume_size)
    data_volume_offering = vol_ops.create_volume_offering(disk_offering_option)
    test_obj_dict.add_disk_offering(data_volume_offering)

    volume_creation_option = test_util.VolumeOption()
    volume_creation_option.set_disk_offering_uuid(data_volume_offering.uuid)
    
    times = 1
    while (times <= target_volume_num):
        try:
            volume_creation_option.set_name('volume-%d' % times)
            volume = test_stub.create_volume(volume_creation_option)
            test_obj_dict.add_volume(volume)
            volume.attach(vm)
        except Exception as e:
            test_util.test_logger("Unexpected volume Creation Failure in storage over provision test. ")
            raise e

        times += 1

    ps_res2 = test_lib.lib_get_storage_capacity(zone_uuids = [zone_uuid])
    avail_cap2 = ps_res2.availableCapacity
    if avail_cap2 > data_volume_size:
        test_util.test_fail('Available disk size: %d is still bigger than offering disk size: %d , after creating %d volumes.' % (avail_cap2, data_volume_size, target_volume_num))
    
    try:
        volume = test_stub.create_volume(volume_creation_option)
        test_obj_dict.add_volume(volume)
    except:
        test_util.test_logger("Expected Volume Creation Failure in storage over provision test. ")
    else:
        test_util.test_fail("The 5th Volume is still created up, which is wrong")

    test_lib.lib_set_provision_storage_rate(original_rate)
    test_lib.lib_robot_cleanup(test_obj_dict)

    test_util.test_pass('Memory Over Provision Test Pass')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
    if original_rate:
        test_lib.lib_set_provision_storage_rate(original_rate)
