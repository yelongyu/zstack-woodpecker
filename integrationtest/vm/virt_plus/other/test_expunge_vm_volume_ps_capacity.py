'''

New Integration Test for expunging KVM VM.

@author: Youyk
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.zstack_test.zstack_test_vm as test_vm_header
import zstackwoodpecker.operations.volume_operations as vol_ops
import time
import os

_config_ = {
        'timeout' : 200,
        'noparallel' : True
        }

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
delete_policy1 = None
delete_policy2 = None

def test():
    global delete_policy1
    global delete_policy2
    delete_policy1 = test_lib.lib_set_delete_policy('vm', 'Delay')
    delete_policy2 = test_lib.lib_set_delete_policy('volume', 'Delay')
    test_util.test_dsc('Test storage capacity when using expunge vm')
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

    host_res = vol_ops.get_local_storage_capacity(host.uuid, ps.uuid)[0]
    avail_cap = host_res.availableCapacity

    vm = test_stub.create_vm(vm_name = 'basic-test-vm', host_uuid = host.uuid)
    test_obj_dict.add_vm(vm)
    data_volume_size = 1024 * 1024 * 10
    disk_offering_option = test_util.DiskOfferingOption()
    disk_offering_option.set_name('test-expunge-data-volume')
    disk_offering_option.set_diskSize(data_volume_size)
    data_volume_offering = vol_ops.create_volume_offering(disk_offering_option)
    test_obj_dict.add_disk_offering(data_volume_offering)

    volume_creation_option = test_util.VolumeOption()
    volume_creation_option.set_disk_offering_uuid(data_volume_offering.uuid)
    
    volume_creation_option.set_name('volume-1')
    volume = test_stub.create_volume(volume_creation_option)
    test_obj_dict.add_volume(volume)
    volume.attach(vm)

    time.sleep(1)
    vm.destroy()
    vm.expunge()
    test_obj_dict.rm_vm(vm)
    volume.delete()
    volume.expunge()
    test_obj_dict.rm_volume(volume)
    host_res2 = vol_ops.get_local_storage_capacity(host.uuid, ps.uuid)[0]
    avail_cap2 = host_res.availableCapacity
    if avail_cap != avail_cap2:
        test_util.test_fail('PS capacity is not same after create/expunge vm/volume on host: %s. Capacity before create vm: %s, after expunge vm: %s ' % (host.uuid, avail_cap, avail_cap2))
    test_lib.lib_set_delete_policy('vm', delete_policy1)
    test_lib.lib_set_delete_policy('volume', delete_policy2)
    test_lib.lib_robot_cleanup(test_obj_dict)
    test_util.test_pass('Expunge VM Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
    test_lib.lib_set_delete_policy('vm', delete_policy1)
    test_lib.lib_set_delete_policy('volume', delete_policy2)
