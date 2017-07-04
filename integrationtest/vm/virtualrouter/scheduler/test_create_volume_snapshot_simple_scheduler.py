'''

New Integration Test for Simple VM stop/start scheduler.

@author: quarkonics
'''

import os
import time
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.vm_operations as vm_ops
import zstackwoodpecker.operations.volume_operations as vol_ops
import zstackwoodpecker.operations.scheduler_operations as schd_ops
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
vm = None
schd_job = None
schd_trigger = None

def query_snapshot_number(volume_uuid):
    cond = res_ops.gen_query_conditions('volumeUuid', '=', volume_uuid)
    return res_ops.query_resource_count(res_ops.VOLUME_SNAPSHOT, cond)

def test():
    global vm
    global schd_job
    global schd_trigger
    vm = test_stub.create_vlan_vm()
    test_obj_dict.add_vm(vm)

    disk_offering = test_lib.lib_get_disk_offering_by_name(os.environ.get('smallDiskOfferingName'))
    volume_creation_option = test_util.VolumeOption()
    volume_creation_option.set_name('volume for snapshot scheduler testing')
    volume_creation_option.set_disk_offering_uuid(disk_offering.uuid)
    volume = test_stub.create_volume(volume_creation_option)
    test_obj_dict.add_volume(volume)

    volume.attach(vm)
    volume.detach()

    test_util.test_dsc('create snapshot and check')

    start_date = int(time.time())
    #sp_option = test_util.SnapshotOption()
    #sp_option.set_name('simple_schduler_snapshot')
    #sp_option.set_volume_uuid(volume.get_volume().uuid)

    schd_job = schd_ops.create_scheduler_job('simple_create_snapshot_scheduler', 'simple_create_snapshot_scheduler', volume.get_volume().uuid, 'volumeSnapshot', None)
    schd_trigger = schd_ops.create_scheduler_trigger('simple_create_snapshot_scheduler', start_date+60, None, 120, 'simple')
    schd_ops.add_scheduler_job_to_trigger(schd_trigger.uuid, schd_job.uuid)
    #schd = vol_ops.create_snapshot_scheduler(sp_option, 'simple', 'simple_create_snapshot_scheduler',  start_date+60, 120)

    snapshot_num = 0
    for i in range(0, 3):
        test_util.test_logger('round %s' % (i))
        test_stub.sleep_util(start_date + 60 + 120*i - 2)
        test_util.test_logger('check volume snapshot number at %s, there should be %s' % (start_date + 60 + 120*i - 2, snapshot_num))
	new_snapshot_num = query_snapshot_number(volume.get_volume().uuid)
	if snapshot_num != new_snapshot_num:
            test_util.test_fail('there sholuld be %s snapshots' % (snapshot_num))
	snapshot_num += 1

        test_stub.sleep_util(start_date + 60 + 120*i + 65)
        test_util.test_logger('check volume snapshot number at %s, there should be %s' % (start_date + 60 + 120*i + 65, snapshot_num))
	new_snapshot_num = query_snapshot_number(volume.get_volume().uuid)
	if snapshot_num != new_snapshot_num:
            test_util.test_fail('there sholuld be %s snapshots' % (snapshot_num))

    schd_ops.del_scheduler_job(schd_job.uuid)
    schd_ops.del_scheduler_trigger(schd_trigger.uuid)
    vm.destroy()
    test_util.test_pass('Create Simple VM Stop Start Scheduler Success')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)

    if schd_job:
	schd_ops.del_scheduler_job(schd_job.uuid)
    if schd_trigger:
	schd_ops.del_scheduler_trigger(schd_trigger.uuid)
