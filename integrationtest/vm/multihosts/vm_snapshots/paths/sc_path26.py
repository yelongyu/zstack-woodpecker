import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", path_list=[
		[TestAction.create_vm, 'vm1', 'flag=sblk'],
		[TestAction.create_volume, 'volume1', 'flag=ceph,scsi'],
		[TestAction.create_volume, 'volume2', 'flag=sblk,scsi'],
		[TestAction.create_volume, 'volume3', 'flag=ceph,scsi'],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot1'],
		[TestAction.create_volume_snapshot, 'volume3', 'volume3-snapshot2'],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot3'],
		[TestAction.create_volume_snapshot, 'volume3', 'volume3-snapshot4'],
		[TestAction.create_volume_snapshot, 'vm1-root', 'vm1-root-snapshot5'],
		[TestAction.create_volume_snapshot, 'vm1-root', 'vm1-root-snapshot6'],
		[TestAction.create_volume_snapshot, 'volume3', 'volume3-snapshot7'],
		[TestAction.create_volume_snapshot, 'volume3', 'volume3-snapshot8'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.use_vm_snapshot, 'vm1-snapshot1'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.use_vm_snapshot, 'vm1-snapshot1'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.reinit_vm, 'vm1'],
		[TestAction.batch_delete_volume_snapshot, ['volume3-snapshot7','volume3-snapshot8',]],
		[TestAction.delete_vm_snapshot, 'vm1-snapshot1'],
		[TestAction.delete_vm_snapshot, 'vm1-snapshot3'],
])



'''
The final status:
Running:[]
Stopped:['vm1']
Enadbled:['volume3-snapshot2', 'volume3-snapshot4', 'vm1-root-snapshot5', 'vm1-root-snapshot6']
attached:[]
Detached:['volume1', 'volume2', 'volume3']
Deleted:['volume3-snapshot7', 'volume3-snapshot8', 'vm1-snapshot1', 'vm1-snapshot3']
Expunged:[]
Ha:[]
Group:
'''