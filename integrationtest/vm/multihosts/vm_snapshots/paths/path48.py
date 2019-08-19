import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", checking_point=8, path_list=[
		[TestAction.create_vm, 'vm1', ],
		[TestAction.create_volume, 'volume1', 'flag=scsi'],
		[TestAction.attach_volume, 'vm1', 'volume1'],
		[TestAction.create_volume, 'volume2', 'flag=scsi'],
		[TestAction.attach_volume, 'vm1', 'volume2'],
		[TestAction.create_volume, 'volume3', 'flag=scsi'],
		[TestAction.attach_volume, 'vm1', 'volume3'],
		[TestAction.create_volume_snapshot, 'volume2', 'volume2-snapshot1'],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot2'],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot6'],
		[TestAction.create_volume_snapshot, 'vm1-root', 'vm1-root-snapshot10'],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot11'],
		[TestAction.create_volume_snapshot, 'vm1-root', 'vm1-root-snapshot15'],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot16'],
		[TestAction.create_volume_snapshot, 'vm1-root', 'vm1-root-snapshot20'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.use_vm_snapshot, 'vm1-snapshot2'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.use_volume_snapshot, 'vm1-root-snapshot10'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.create_vm_backup, 'vm1', 'vm1-backup1'],
		[TestAction.delete_volume_snapshot, 'vm1-snapshot6'],
		[TestAction.delete_volume_snapshot, 'volume3-snapshot2'],
		[TestAction.batch_delete_snapshots, ['vm1-root-snapshot20','volume1-snapshot2',]],
])



'''
The final status:
Running:['vm1']
Stopped:[]
Enadbled:['volume2-snapshot1', 'vm1-snapshot2', 'volume2-snapshot2', 'volume1-snapshot6', 'volume2-snapshot6', 'volume3-snapshot6', 'vm1-root-snapshot10', 'vm1-snapshot11', 'volume1-snapshot11', 'volume2-snapshot11', 'volume3-snapshot11', 'vm1-root-snapshot15', 'vm1-snapshot16', 'volume1-snapshot16', 'volume2-snapshot16', 'volume3-snapshot16', 'vm1-backup1', 'volume1-backup1', 'volume2-backup1', 'volume3-backup1']
attached:['volume1', 'volume2', 'volume3']
Detached:[]
Deleted:['vm1-snapshot6', 'volume3-snapshot2', 'vm1-root-snapshot20', 'volume1-snapshot2']
Expunged:[]
Ha:[]
Group:
	vm_snap3:['vm1-snapshot11', 'volume1-snapshot11', 'volume2-snapshot11', 'volume3-snapshot11']---vm1volume1_volume2_volume3
	vm_backup1:['vm1-backup1', 'volume1-backup1', 'volume2-backup1', 'volume3-backup1']---vm1_volume1_volume2_volume3
	vm_snap4:['vm1-snapshot16', 'volume1-snapshot16', 'volume2-snapshot16', 'volume3-snapshot16']---vm1volume1_volume2_volume3
'''
