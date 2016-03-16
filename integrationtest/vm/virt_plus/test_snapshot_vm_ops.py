'''

Do snapshot on VM root volume and do some vm ops with expunge

This case is coming from a bug.

@author: Youyk
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.zstack_test.zstack_test_snapshot as zstack_sp_header
import zstackwoodpecker.zstack_test.zstack_test_volume as zstack_vol_header
import zstackwoodpecker.header.volume as vol_header

import os
import time

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def test():
    if conf_ops.get_global_config_value('vm', 'deletionPolicy') == 'Direct' :
        test_util.test_skip('vm delete_policy is Direct, skip test.')
        return
    test_util.test_dsc('Create original vm')
    vm = test_stub.create_vm(vm_name = 'basic-test-vm')
    test_obj_dict.add_vm(vm)

    root_volume_uuid = test_lib.lib_get_root_volume_uuid(vm.get_vm())
    test_util.test_dsc('Stop vm before create snapshot.')
    vm.stop()

    test_util.test_dsc('create snapshot and check')
    snapshots = test_obj_dict.get_volume_snapshot(root_volume_uuid)

    snapshots.create_snapshot('create_root_snapshot1')
    test_util.test_dsc('start vm')
    vm.destroy()
    vm.recover()
    vm.start()
    vm.destroy()
    vm.expunge()
    test_lib.lib_robot_cleanup(test_obj_dict)
    test_util.test_pass('Do snapshot ops on VM root volume with VM ops successfully')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
