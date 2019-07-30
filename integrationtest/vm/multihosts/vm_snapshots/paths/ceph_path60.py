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
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot1'],
		[TestAction.clone_vm, 'vm1', 'vm2', 'full'],
		[TestAction.detach_volume, 'volume5'],
		[TestAction.create_vm_snapshot, 'vm2', 'vm2-snapshot5'],
		[TestAction.create_volume_backup, 'vm1-root', 'vm1-root-backup1'],
		[TestAction.create_vm_snapshot, 'vm2', 'vm2-snapshot8'],
		[TestAction.clone_vm, 'vm2', 'vm3'],
		[TestAction.create_volume_backup, 'volume2', 'volume2-backup2'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.use_volume_backup, 'volume2-backup2'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.create_volume_snapshot, 'vm1-root', 'vm1-root-snapshot11'],
		[TestAction.delete_vm_snapshot, 'vm1-snapshot1'],
])



'''
The final status:
Running:['vm2', 'vm3', 'vm1']
Stopped:[]
Enadbled:['vm2-snapshot5', 'volume4-snapshot5', 'volume6-snapshot5', 'vm2-snapshot8', 'volume4-snapshot8', 'volume6-snapshot8', 'vm1-root-snapshot11', 'vm1-root-backup1', 'volume2-backup2']
attached:['volume1', 'volume2', 'volume3', 'volume4', 'volume6']
Detached:['volume5']
Deleted:['vm1-snapshot1', 'volume1-snapshot1', 'volume2-snapshot1', 'volume3-snapshot1']
Expunged:[]
Ha:[]
Group:
	vm_snap2:['vm2-snapshot5', 'volume4-snapshot5', 'volume6-snapshot5']---vm2volume4_volume6
	vm_snap3:['vm2-snapshot8', 'volume4-snapshot8', 'volume6-snapshot8']---vm2volume4_volume6
'''