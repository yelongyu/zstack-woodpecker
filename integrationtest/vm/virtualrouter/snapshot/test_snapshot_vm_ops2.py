'''

Do complex snapshot ops on VM root volume. The chain might be broken. 

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

    vm_root_volume_inv = test_lib.lib_get_root_volume(vm.get_vm())
    root_volume_uuid = vm_root_volume_inv.uuid 
    test_util.test_dsc('Stop vm before create snapshot.')
    vm.stop()

    test_util.test_dsc('create snapshot and check')
    snapshots = test_obj_dict.get_volume_snapshot(root_volume_uuid)
    snapshots.set_utility_vm(vm1)

    vm1.check()

    #create snapshot1 from VM's root volume
    snapshot1 = snapshots.create_snapshot('create_root_snapshot1')

    #create new data volume from last root volume's snapshot1
    volume2 = snapshot1.create_data_volume('data_volume_for_root')
    test_obj_dict.add_volume(volume2)

    ##backup snapshot1
    #snapshots.backup_snapshot(snapshot1)

    ##delete backuped snapshot1
    #snapshots.delete_backuped_snapshot(snapshot1)

    snapshots2 = test_obj_dict.get_volume_snapshot(volume2.get_volume().uuid)
    snapshots2.set_utility_vm(vm1)

    #create snapshot2 from new created data volume
    snapshot2 = snapshots2.create_snapshot('create_data_snapshot2')
    snapshots.use_snapshot(snapshot1)

    #create 2nd data volume3 from previous root volume snapshot!
    volume3 = snapshot1.create_data_volume('data_volume_for_root2')

    #Delete the snapshot2
    snapshots2.delete_snapshot(snapshot2)

    #Create snaphot5 from new created data volume
    #In the bug, this operation will fail, when doing volume attach.
    snapshots2.create_snapshot('create_root_snapshot5')

    #snapshots2.backup_snapshot(snapshots2.get_current_snapshot())
    #snapshots2.delete_backuped_snapshot(snapshots2.get_current_snapshot())

    snapshots2.check()
    snapshots.check()

    test_lib.lib_robot_cleanup(test_obj_dict)
    test_util.test_pass('Do snapshot ops on VM root volume with VM ops successfully')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
