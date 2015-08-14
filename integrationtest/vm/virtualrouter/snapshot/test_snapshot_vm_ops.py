'''

Do snapshot on VM root volume and do some vm ops, like vm start/stop

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
    test_util.test_dsc('Create original vm')
    vm = test_stub.create_vlan_vm()
    test_obj_dict.add_vm(vm)
    vm1 = test_stub.create_vlan_vm()
    test_obj_dict.add_vm(vm1)

    root_volume_uuid = test_lib.lib_get_root_volume_uuid(vm.get_vm())
    test_util.test_dsc('Stop vm before create snapshot.')
    vm.stop()

    test_util.test_dsc('create snapshot and check')
    snapshots = test_obj_dict.get_volume_snapshot(root_volume_uuid)
    snapshots.set_utility_vm(vm1)
    vm1.check()

    snapshots.create_snapshot('create_root_snapshot1')
    volume2 = snapshots.get_current_snapshot().create_data_volume('data_volume_for_root')
    test_obj_dict.add_volume(volume2)
    snapshots2 = test_obj_dict.get_volume_snapshot(volume2.get_volume().uuid)
    snapshots2.set_utility_vm(vm1)
    snapshots2.create_snapshot('create_root_snapshot2')
    snapshots2.use_snapshot(snapshots2.get_current_snapshot())
    #snapshots2.backup_snapshot(snapshots2.get_current_snapshot())
    #snapshots2.delete_backuped_snapshot(snapshots2.get_current_snapshot())

    volume2.attach(vm)
    volume2.detach()
    snapshots.delete_snapshot(snapshots.get_current_snapshot())

    test_util.test_dsc('start vm')
    vm.start()

    test_lib.lib_robot_cleanup(test_obj_dict)
    test_util.test_pass('Do snapshot ops on VM root volume with VM ops successfully')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
