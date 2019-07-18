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
		[TestAction.create_volume_snapshot, 'volume2', 'volume2-snapshot2'],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot3'],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot7'],
		[TestAction.create_volume_snapshot, 'volume3', 'volume3-snapshot11'],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot12'],
		[TestAction.create_volume_snapshot, 'volume1', 'volume1-snapshot16'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.use_volume_snapshot, 'volume1-snapshot3'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.use_volume_snapshot, 'vm1-root-snapshot1'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.use_volume_snapshot, 'volume1-snapshot3'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.reboot_vm, 'vm1'],
		TestAction.batch_delete_snapshots, ['volume2-snapshot2','volume1-snapshot7',],
		[TestAction.delete_vm_snapshot, 'vm1-snapshot3'],
		[TestAction.delete_volume_snapshot, 'volume1-snapshot12'],
])



'''
The final status:
Running:['vm1']
Stopped:[]
Enadbled:['vm1-root-snapshot1', 'vm1-snapshot7', 'volume2-snapshot7', 'volume3-snapshot7', 'volume3-snapshot11', 'vm1-snapshot12', 'volume2-snapshot12', 'volume3-snapshot12', 'volume1-snapshot16']
attached:['volume1', 'volume2', 'volume3']
Detached:[]
Deleted:['volume2-snapshot2', 'volume1-snapshot7', 'vm1-snapshot3', 'volume1-snapshot3', 'volume2-snapshot3', 'volume3-snapshot3', 'volume1-snapshot12']
Expunged:[]
Ha:[]
Group:
	vm_snap3:['vm1-snapshot12', 'volume1-snapshot12', 'volume2-snapshot12', 'volume3-snapshot12']---vm1volume1_volume2_volume3
'''