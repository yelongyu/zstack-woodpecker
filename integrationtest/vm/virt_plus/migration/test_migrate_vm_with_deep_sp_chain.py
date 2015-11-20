'''

Test vm migration with deep snapshot chain. 

@author: Youyk
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.zstack_test.zstack_test_snapshot as zstack_sp_header

import os
import time

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def test():
    test_util.test_dsc('Create test vm as utility vm')
    vm = test_stub.create_vm(vm_name = 'migrate_vm_with_snapshot')
    test_obj_dict.add_vm(vm)

    root_volume_uuid = test_lib.lib_get_root_volume_uuid(vm.get_vm())
    test_util.test_dsc('create snapshot and check')
    snapshots = test_obj_dict.get_volume_snapshot(root_volume_uuid)
    snapshots.set_utility_vm(vm)

    times = 44
    while times > 0 :
        vm.stop()
        snapshot = snapshots.create_snapshot('create_snapshot_%s' % (44 - times))
        vm.start()
        if times == 22:
            snapshot1 = snapshots.get_current_snapshot()
        times = times - 1

    test_util.test_dsc('migrate vm and check snapshot')
    test_stub.migrate_vm_to_random_host(vm)
    vm.check()
    snapshots.check()

    vm.stop()
    snapshots.use_snapshot(snapshot1)
    vm.start()
    snapshots.check()
    vm.check()

    test_util.test_dsc('migrate vm and check snapshot')
    test_stub.migrate_vm_to_random_host(vm)
    vm.check()
    snapshots.check()

    snapshots.delete()
    test_obj_dict.rm_volume_snapshot(snapshots)
    vm.destroy()
    test_util.test_pass('Create deep Snapshot chain with VM migration test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
