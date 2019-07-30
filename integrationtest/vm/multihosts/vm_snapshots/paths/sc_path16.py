import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", path_list=[
		[TestAction.create_vm, 'vm1', 'flag=sblk'],
		[TestAction.create_volume, 'volume1', 'flag=ceph,scsi'],
		[TestAction.create_volume, 'volume2', 'flag=sblk,scsi'],
		[TestAction.create_volume, 'volume3', 'flag=ceph,scsi'],
		[TestAction.create_volume_snapshot, 'volume2', 'volume2-snapshot1'],
		[TestAction.create_volume_snapshot, 'vm1-root', 'vm1-root-snapshot2'],
		[TestAction.create_volume_snapshot, 'volume2', 'volume2-snapshot3'],
		[TestAction.create_volume_snapshot, 'vm1-root', 'vm1-root-snapshot4'],
		[TestAction.create_volume_snapshot, 'volume2', 'volume2-snapshot5'],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot6'],
		[TestAction.create_volume_snapshot, 'volume1', 'volume1-snapshot7'],
		[TestAction.use_volume_snapshot, 'volume2-snapshot1'],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot8'],
		[TestAction.use_volume_snapshot, 'volume1-snapshot7'],
		[TestAction.reboot_vm, 'vm1'],
		[TestAction.delete_vm_snapshot, 'vm1-snapshot6'],
		[TestAction.batch_delete_volume_snapshot, ['volume2-snapshot3','vm1-root-snapshot2',]],
		[TestAction.delete_volume_snapshot, 'volume2-snapshot1'],
])



'''
The final status:
Running:['vm1']
Stopped:[]
Enadbled:['vm1-root-snapshot4', 'volume2-snapshot5', 'volume1-snapshot7', 'vm1-snapshot8']
attached:[]
Detached:['volume1', 'volume2', 'volume3']
Deleted:['vm1-snapshot6', 'volume2-snapshot3', 'vm1-root-snapshot2', 'volume2-snapshot1']
Expunged:[]
Ha:[]
Group:
	vm_snap2:['vm1-snapshot8']---vm1
'''