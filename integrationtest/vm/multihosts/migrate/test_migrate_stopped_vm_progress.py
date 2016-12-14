'''

New Integration test for testing stopped vm migration between hosts.

@author: quarkonics
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.volume_operations as vol_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import apibinding.inventory as inventory
import threading
import time

vm = None
test_stub = test_lib.lib_get_test_stub()

def migrate_volume(volume_uuid, target_host_uuid):
    vol_ops.migrate_volume(volume_uuid, target_host_uuid)

def test():
    global vm
    vm = test_stub.create_vr_vm('migrate_stopped_vm', 'imageName_s', 'l3VlanNetwork2')
    ps = test_lib.lib_get_primary_storage_by_uuid(vm.get_vm().allVolumes[0].primaryStorageUuid)
    if ps.type != inventory.LOCAL_STORAGE_TYPE:
        test_util.test_skip('Skip test on non-localstorage')
    target_host = test_lib.lib_find_random_host(vm.vm)
    vm.stop()
    thread = threading.Thread(target=migrate_volume, args=(vm.get_vm().allVolumes[0].uuid, target_host.uuid, ))
    thread.start()
    time.sleep(5)
    progress = res_ops.get_task_progress(vm.get_vm().allVolumes[0].uuid)
    if len(progress.taskProgress) > 1:
        test_util.test_fail("only 1 progress expected for given uuid")

    if int(progress.taskProgress[0].progress) < 0 or int(progress.taskProgress[0].progress) > 100:
        test_util.test_fail("Progress of task should be between 0 and 100, while it actually is %s" % (progress.taskProgress[0].progress))
    thread.join()

    vm.destroy()
    test_util.test_pass('Migrate Stopped VM Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global vm
    if vm:
        try:
            vm.destroy()
        except:
            pass
