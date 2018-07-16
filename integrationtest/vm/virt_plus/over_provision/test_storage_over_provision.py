'''
This case can not execute parallelly
@author: Youyk
'''
import os
import time
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.host_operations as host_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.vm_operations as vm_ops
import zstackwoodpecker.operations.volume_operations as vol_ops
import zstacklib.utils.sizeunit as sizeunit

_config_ = {
        'timeout' : 1000,
        'noparallel' : True
        }

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
original_rate = None

def test():
    global res
    global original_rate
    test_util.test_dsc('Test storage over provision method')
    primary_storage_list = res_ops.query_resource(res_ops.PRIMARY_STORAGE)
    for ps in primary_storage_list:
        if ps.type == "SharedBlock":
            test_util.test_skip('SharedBlock primary storage does not support overProvision')

    test_lib.lib_skip_if_ps_num_is_not_eq_number(1)
    zone_uuid = res_ops.query_resource(res_ops.ZONE)[0].uuid
    cond = res_ops.gen_query_conditions('state', '=', 'Enabled')
    cond = res_ops.gen_query_conditions('status', '=', 'Connected', cond)
    host = res_ops.query_resource_with_num(res_ops.HOST, cond, limit = 1)
    if not host:
        test_util.test_skip('No Enabled/Connected host was found, skip test.' )
        return True

    ps = res_ops.query_resource_with_num(res_ops.PRIMARY_STORAGE, cond, limit = 1)
    if not ps:
        test_util.test_skip('No Enabled/Connected primary storage was found, skip test.' )
        return True

    host = host[0]
    ps = ps[0]
    ps_type = ps.type
    #TODO: Fix ceph testing
    if ps_type == 'Ceph' or ps_type == 'SharedMountPoint':
        test_util.test_skip('skip test for ceph and smp.')

    over_provision_rate = 2.5
    target_volume_num = 12
    kept_disk_size = 10 * 1024 * 1024

    
    vm = test_stub.create_vm(vm_name = 'storage_over_prs_vm_1', \
                    host_uuid = host.uuid)
    test_obj_dict.add_vm(vm)
    vm.check()

    avail_cap = get_storage_capacity(ps_type, host.uuid, ps.uuid)
    if avail_cap < kept_disk_size:
        test_util.test_skip('available disk capacity:%d is too small, skip test.' % avail_cap)
        return True
    res = sizeunit.get_size(test_lib.lib_get_reserved_primary_storage())
    original_rate = test_lib.lib_set_provision_storage_rate(over_provision_rate)
    #data_volume_size = int(over_provision_rate * (avail_cap - kept_disk_size) / target_volume_num)   
    data_volume_size = int(over_provision_rate * (avail_cap - res )/ target_volume_num)
    #will change the rate back to check if available capacity is same with original one. This was a bug, that only happened when system create 1 vm.
    test_lib.lib_set_provision_storage_rate(original_rate)
    avail_cap_tmp = get_storage_capacity(ps_type, host.uuid, ps.uuid)
    if avail_cap != avail_cap_tmp:
        test_util.test_fail('disk size is not same, between 2 times provision. Before change over rate, 1st cap: %d; 2nd cap: %d' % (avail_cap, avail_cap_tmp))

    test_lib.lib_set_provision_storage_rate(over_provision_rate)
    test_util.test_logger('Will create a serial of volume. Each of them will have %d size.' % data_volume_size)
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
            test_util.test_logger('Current available storage size: %d' % get_storage_capacity(ps_type, host.uuid, ps.uuid))
            volume.attach(vm)
        except Exception as e:
            test_util.test_logger("Unexpected volume Creation Failure in storage over provision test. ")
            raise e

        times += 1

    time.sleep(2)
    avail_cap2 = (get_storage_capacity(ps_type, host.uuid, ps.uuid)-res)
    if avail_cap2 > data_volume_size:
        test_util.test_fail('Available disk size: %d is still bigger than offering disk size: %d , after creating %d volumes.' % (avail_cap2, data_volume_size, target_volume_num))
    
    try:
        volume_creation_option.set_name('volume-%d' % (times + 1))
        volume = test_stub.create_volume(volume_creation_option)
        test_obj_dict.add_volume(volume)
        volume.attach(vm)
    except:
        test_util.test_logger("Expected Volume Creation Failure in storage over provision test. ")
    else:
        test_util.test_fail("The %dth Volume is still attachable, which is wrong"% (target_volume_num + 1))

    test_lib.lib_set_provision_storage_rate(original_rate)
    test_lib.lib_robot_cleanup(test_obj_dict)

    test_util.test_pass('Memory Over Provision Test Pass')

def get_storage_capacity(ps_type, host_uuid, ps_uuid):
    if ps_type == 'LocalStorage':
        host_res = vol_ops.get_local_storage_capacity(host_uuid, ps_uuid)[0]
    else:
        host_res = test_lib.lib_get_storage_capacity(ps_uuids=[ps_uuid])
    return host_res.availableCapacity

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
    if original_rate:
        test_lib.lib_set_provision_storage_rate(original_rate)
