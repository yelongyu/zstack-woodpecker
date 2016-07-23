'''
This case can not execute parallelly.

This case will calculate max available VMs base on 1 host available disk space.

The it will try to create all VMs at the same time to see if zstack could 
handle it. 
@author: Youyk
'''
import os
import sys
import threading
import time
import random

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.host_operations as host_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.vm_operations as vm_ops
import zstackwoodpecker.operations.volume_operations as vol_ops
import zstacklib.utils.sizeunit as sizeunit
import apibinding.inventory as inventory

_config_ = {
    'timeout' : 1000,
    'noparallel' : True
}

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
original_rate = None
new_offering_uuid = None
exc_info = []

def parallelly_create_vm(vm_name, image_name, host_uuid, disk_offering_uuid):
    try:
        vm = test_stub.create_vm(vm_name = vm_name, \
                image_name = image_name, \
                host_uuid = host_uuid, \
                disk_offering_uuids = [disk_offering_uuid])
        test_obj_dict.add_vm(vm)
    except Exception as e:
        exc_info.append(sys.exc_info())

def check_thread_exception():
    if exc_info:
        info1 = exc_info[0][1]
        info2 = exc_info[0][2]
        raise info1, None, info2

def test():
    global original_rate
    global new_offering_uuid
    global delete_policy
    test_util.test_dsc('Test memory allocation and reclaiming.')
    cond = res_ops.gen_query_conditions('state', '=', 'Enabled')
    cond = res_ops.gen_query_conditions('status', '=', 'Connected', cond)
    hosts = res_ops.query_resource_with_num(res_ops.HOST, cond)
    if not hosts:
        test_util.test_skip('No Enabled/Connected host was found, skip test.' )
        return True

    ps = res_ops.query_resource_with_num(res_ops.PRIMARY_STORAGE, cond, limit = 1)
    if not ps:
        test_util.test_skip('No Enabled/Connected primary storage was found, skip test.' )
        return True

    if ps[0].type == inventory.CEPH_PRIMARY_STORAGE_TYPE or ps[0].type == 'SharedMountPoint':
        test_util.test_skip('skip test on ceph and smp.' )
        return True

    host = random.choice(hosts)
    ps = ps[0]
    over_provision_rate = 1
    target_vm_num = 5

    host_res = vol_ops.get_local_storage_capacity(host.uuid, ps.uuid)[0]
    avail_cap = host_res.availableCapacity

    image_name = os.environ.get('imageName_net')
    image = test_lib.lib_get_image_by_name(image_name)
    image_size = image.size

    original_rate = test_lib.lib_set_provision_storage_rate(over_provision_rate)
    data_volume_size = int(avail_cap / target_vm_num * over_provision_rate - image_size)
    if data_volume_size < 0:
        test_util.test_skip('Do not have enough disk space to do test')
        return True

    delete_policy = test_lib.lib_set_delete_policy('vm', 'Direct')
    delete_policy = test_lib.lib_set_delete_policy('volume', 'Direct')

    host_res = vol_ops.get_local_storage_capacity(host.uuid, ps.uuid)[0]
    avail_cap = host_res.availableCapacity

    disk_offering_option = test_util.DiskOfferingOption()
    disk_offering_option.set_name('vm-parallel-creation-test')
    disk_offering_option.set_diskSize(data_volume_size)
    data_volume_offering = vol_ops.create_volume_offering(disk_offering_option)
    test_obj_dict.add_disk_offering(data_volume_offering)

    rounds = 1
    while (rounds <= 3):
        times = 1
        test_util.test_logger('test round: %s' % rounds)
        while (times <= (target_vm_num)):
            thread = threading.Thread(target = parallelly_create_vm, \
                    args = ('parallel_vm_creating_%d' % times, \
                        image_name, \
                        host.uuid, \
                        data_volume_offering.uuid, ))
            thread.start()

            times += 1

        times = 1
        print 'Running VM: %s ' % len(test_obj_dict.get_vm_list())
        while threading.active_count() > 1:
            check_thread_exception()
            time.sleep(1)
            if times > 30:
                test_util.test_fail('creating vm time exceed 30s')
            times += 1

        check_thread_exception()
        try:
            vm = test_stub.create_vm(vm_name = 'unexpected vm', \
                    image_name = image_name, \
                    host_uuid = host.uuid)
            test_obj_dict.add_vm(vm)
        except:
            test_util.test_logger('expect vm creation failure')
        else:
            test_util.test_fail('The extra vm is unexpected to be created up')

        for vm in test_obj_dict.get_all_vm_list():
            try:
                test_lib.lib_destroy_vm_and_data_volumes_objs_update_test_dict(vm, test_obj_dict)
            except Exception as e:
                test_util.test_logger("VM Destroying Failure in vm parallel creation test. :%s " % e)
                raise e

        rounds += 1
    
    test_lib.lib_set_provision_storage_rate(original_rate)
    test_lib.lib_robot_cleanup(test_obj_dict)
    test_lib.lib_set_delete_policy('vm', delete_policy)
    test_lib.lib_set_delete_policy('volume', delete_policy)

    test_util.test_pass('Parallel vm creation Test Pass')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
    if original_rate:
        test_lib.lib_set_provision_storage_rate(original_rate)
    test_lib.lib_set_delete_policy('vm', delete_policy)
    test_lib.lib_set_delete_policy('volume', delete_policy)
