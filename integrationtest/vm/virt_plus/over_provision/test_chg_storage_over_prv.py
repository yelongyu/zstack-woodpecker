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
import apibinding.inventory as inventory

_config_ = {
        'timeout' : 1000,
        'noparallel' : True
        }

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
original_rate = None

def test():
    global original_rate
    test_util.test_dsc('Test change storage over provision rate method')
    zone_uuid = res_ops.query_resource(res_ops.ZONE)[0].uuid
    cond = res_ops.gen_query_conditions('state', '=', 'Enabled')
    cond = res_ops.gen_query_conditions('status', '=', 'Connected', cond)
    host = res_ops.query_resource_with_num(res_ops.HOST, cond, limit = 1)
    if not host:
        test_util.test_skip('No Enabled/Connected host was found, skip test.' )
        return True

    host = host[0]
    over_provision_rate1 = 2.5
    over_provision_rate2 = 1.5
    target_volume_num = 12
    kept_disk_size = 10 * 1024 * 1024

    vm = test_stub.create_vm(vm_name = 'storage_over_prs_vm_1', \
                    host_uuid = host.uuid)
    vm.check()
    test_obj_dict.add_vm(vm)

    cond = res_ops.gen_query_conditions('state', '=', 'Enabled')
    cond = res_ops.gen_query_conditions('status', '=', 'Connected', cond)

    ps = res_ops.query_resource_with_num(res_ops.PRIMARY_STORAGE, cond, limit = 2)
    if not ps:
        test_util.test_skip('No Enabled/Connected primary storage was found, skip test.' )
        return True

    ps1 = ps[0].uuid
    ps2 = ps[1].uuid


    ps1_res = test_lib.lib_get_storage_capacity(ps_uuids=[ps1])
    ps2_res = test_lib.lib_get_storage_capacity(ps_uuids=[ps2])
    avail_cap = ps1_res.availableCapacity + ps2_res.availableCapacity
    test_util.test_dsc("ps1[uuid:%s]'s available capacity is %s" % (ps1, ps1_res.availableCapacity))
    test_util.test_dsc("ps2[uuid:%s]'s available capacity is %s" % (ps2, ps2_res.availableCapacity))
    if avail_cap < kept_disk_size:
        test_util.test_skip('available disk capacity:%d is too small, skip test.' % avail_cap)
        return True

    pss = res_ops.query_resource_with_num(res_ops.PRIMARY_STORAGE, cond)
    for ps in pss:
        if ps.type == inventory.CEPH_PRIMARY_STORAGE_TYPE or ps.type == 'SharedMountPoint':
            test_util.test_skip('skip test on ceph and smp.' )

    original_rate = test_lib.lib_set_provision_storage_rate(over_provision_rate1)
    data_volume_size = int(over_provision_rate1 * (avail_cap - kept_disk_size) / target_volume_num)
    disk_offering_option = test_util.DiskOfferingOption()
    disk_offering_option.set_name('storage-over-ps-test')
    disk_offering_option.set_diskSize(data_volume_size)
    data_volume_offering = vol_ops.create_volume_offering(disk_offering_option)
    test_obj_dict.add_disk_offering(data_volume_offering)

    volume_creation_option = test_util.VolumeOption()
    volume_creation_option.set_disk_offering_uuid(data_volume_offering.uuid)
    
    volume_creation_option.set_name('volume-1')
    volume1 = test_stub.create_volume(volume_creation_option)
    test_obj_dict.add_volume(volume1)
    #res = test_lib.lib_get_storage_capacity(zone_uuids = [zone_uuid])
    #test_util.test_logger('Current available storage size: %d' % res.availableCapacity)
    volume1.attach(vm)

    test_lib.lib_set_provision_storage_rate(over_provision_rate2)
    volume_creation_option.set_name('volume-2')
    volume2 = test_stub.create_volume(volume_creation_option)
    test_obj_dict.add_volume(volume2)
    #res = test_lib.lib_get_storage_capacity(zone_uuids = [zone_uuid])
    #test_util.test_logger('Current available storage size: %d' % res.availableCapacity)
    volume2.attach(vm)
    volume1.delete()
    volume1.expunge()

    test_lib.lib_set_provision_storage_rate(over_provision_rate1)
    volume2.delete()
    volume2.expunge()

    test_lib.lib_set_provision_storage_rate(original_rate)
    time.sleep(10)
    ps1_res2 = test_lib.lib_get_storage_capacity(ps_uuids=[ps1])
    ps2_res2 = test_lib.lib_get_storage_capacity(ps_uuids=[ps2])
    test_util.test_dsc("ps1[uuid:%s]'s available capacity is %s" % (ps1, ps1_res.availableCapacity))
    test_util.test_dsc("ps2[uuid:%s]'s available capacity is %s" % (ps2, ps2_res.availableCapacity))

    avail_cap2 = ps1_res2.availableCapacity + ps2_res2.availableCapacity
    if avail_cap2 != avail_cap:
        test_util.test_fail('Available disk size: %d is different with original size: %d, after creating volume under different over rate.' % (avail_cap2, avail_cap))
    
    test_lib.lib_robot_cleanup(test_obj_dict)
    test_util.test_pass('Memory Over Provision Test Pass')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
    if original_rate:
        test_lib.lib_set_provision_storage_rate(original_rate)
