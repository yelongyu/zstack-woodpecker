'''

New Integration test for testing stopped vm migration between hosts.

@author: quarkonics
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.volume_operations as vol_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import apibinding.inventory as inventory
import threading
import time
import uuid
threads_num = 3
vms = [None] * threads_num
threads = [None] * threads_num
migrate_jobs = [None] * threads_num
threads_result = [None] * threads_num
checker_threads = [None] * threads_num
checker_threads_result = [None] * threads_num
test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def migrate_volume(index):
    target_host = test_lib.lib_find_random_host(vms[index].get_vm())
    vms[index].stop()
    migrate_jobs[index] = str(uuid.uuid4()).replace('-', '')
    threads_result[index] = "Start"
    vol_ops.migrate_volume_apiid(vms[index].get_vm().allVolumes[0].uuid, target_host.uuid, migrate_jobs[index])
    threads_result[index] = "Done"

def check_migrate_volume_progress(index):
    for i in range(0, 2400):
        if threads_result[index] == None:
            time.sleep(0.1)
            continue

    for i in range(0, 3600):
        progresses = res_ops.get_progress(migrate_jobs[index])
        if len(progresses) > 0 :
            break
        time.sleep(0.1)
    if len(progresses) <= 0:
        test_util.test_fail("volume not start migrating in 360 seconds")

    progress = progresses[0]

    if int(progress.content) < 0 or int(progress.content) > 100:
        test_util.test_fail("Progress of task should be between 0 and 100, while it actually is %s" % (progress.content))

    for i in range(0, 3600):
        last_progress = progress
        progresses = res_ops.get_progress(migrate_jobs[index])
        if len(progresses) <= 0:
            break
        progress = progresses[0]

        if int(progress.content) < int(last_progress.content):
            test_util.test_fail("Progress of task (%s) %s is smaller than last time %s" % (migrate_jobs[index], progress.content, last_progress.content))
        time.sleep(0.1)

#    vms[index].update()
#    if vms[index].get_vm().allVolumes[0].status != 'Migrating':
#        test_util.test_fail("Volume should be ready when no progress anymore")
    vms[index].start()
    checker_threads_result[index] = "Done"

def test():
    global vms
    for i in range(0, threads_num):
        vms[i] = test_stub.create_vr_vm('migrate_stopped_vm', 'imageName_net', 'l3VlanNetwork2')
        test_obj_dict.add_vm(vms[i])
        ps = test_lib.lib_get_primary_storage_by_uuid(vms[i].get_vm().allVolumes[0].primaryStorageUuid)
        if ps.type != inventory.LOCAL_STORAGE_TYPE:
            test_util.test_skip('Skip test on non-localstorage')

    for i in range(0, threads_num):
        threads[i] = threading.Thread(target=migrate_volume, args=(i, ))
        threads[i].start()

    for i in range(0, threads_num):
        checker_threads[i] = threading.Thread(target=check_migrate_volume_progress, args=(i, ))
        checker_threads[i].start()

    for i in range(0, threads_num):
        checker_threads[i].join()
        threads[i].join()

    for i in range(0, threads_num):
        if threads_result[i] != "Done":
            test_util.test_fail("Exception happened during migrate Volume")
        if checker_threads_result[i] != "Done":
            test_util.test_fail("Exception happened during check migrate Volume progress")

    for i in range(0, threads_num):
        vms[i].destroy()
        vms[i].expunge()

    test_util.test_pass('Migrate Stopped VM progress Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global vms
    test_lib.lib_error_cleanup(test_obj_dict)
