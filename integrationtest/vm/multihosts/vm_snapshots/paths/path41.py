import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", path_list=[
		[TestAction.create_vm, 'vm1', ],
		[TestAction.create_volume, 'volume1', 'flag=scsi'],
		[TestAction.attach_volume, 'vm1', 'volume1'],
		[TestAction.create_volume, 'volume2', 'flag=scsi'],
		[TestAction.attach_volume, 'vm1', 'volume2'],
		[TestAction.create_volume, 'volume3', 'flag=scsi'],
		[TestAction.attach_volume, 'vm1', 'volume3'],
		[TestAction.create_volume_snapshot, 'vm1-root', 'vm1-root-snapshot1'],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot2'],
		[TestAction.create_volume_snapshot, 'vm1-root', 'vm1-root-snapshot6'],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot7'],
		[TestAction.create_volume_snapshot, 'volume1', 'volume1-snapshot11'],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot12'],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot16'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.use_volume_snapshot, 'vm1-snapshot7'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.use_volume_snapshot, 'vm1-snapshot7'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.use_volume_snapshot, 'vm1-snapshot12'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.reinit_vm, 'vm1'],
		[TestAction.delete_volume_snapshot, 'volume3-snapshot2'],
		[TestAction.delete_volume_snapshot, 'volume3-snapshot7'],
		[TestAction.batch_delete_snapshots, ['volume2-snapshot2','vm1-snapshot12',]],
])



'''
The final status:
Running:[]
Stopped:['vm1']
Enadbled:['vm1-root-snapshot1', 'vm1-snapshot2', 'volume1-snapshot2', 'vm1-root-snapshot6', 'vm1-snapshot7', 'volume1-snapshot7', 'volume2-snapshot7', 'volume1-snapshot11', 'volume1-snapshot12', 'volume2-snapshot12', 'volume3-snapshot12', 'vm1-snapshot16', 'volume1-snapshot16', 'volume2-snapshot16', 'volume3-snapshot16']
attached:['volume1', 'volume2', 'volume3']
Detached:[]
Deleted:['volume3-snapshot2', 'volume3-snapshot7', 'volume2-snapshot2', 'vm1-snapshot12']
Expunged:[]
Ha:[]
Group:
	vm_snap2:['vm1-snapshot7', 'volume1-snapshot7', 'volume2-snapshot7', 'volume3-snapshot7']---vm1volume1_volume2_volume3
	vm_snap4:['vm1-snapshot16', 'volume1-snapshot16', 'volume2-snapshot16', 'volume3-snapshot16']---vm1volume1_volume2_volume3
'''