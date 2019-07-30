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
		[TestAction.clone_vm, 'vm1', 'vm2'],
		[TestAction.detach_volume, 'volume3'],
		[TestAction.create_vm_snapshot, 'vm2', 'vm2-snapshot5'],
		[TestAction.stop_vm, 'vm2'],
		[TestAction.ps_migrate_vm, 'vm2'],
		[TestAction.start_vm, 'vm2'],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot6'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.ps_migrate_vm, 'vm1'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.attach_volume, 'vm2', 'volume3'],
		[TestAction.create_vm_backup, 'vm1', 'vm1-backup1'],
		[TestAction.delete_vm_snapshot, 'vm2-snapshot5'],
])



'''
The final status:
Running:['vm2', 'vm1']
Stopped:[]
Enadbled:['vm1-snapshot1', 'volume1-snapshot1', 'volume2-snapshot1', 'volume3-snapshot1', 'vm1-snapshot6', 'volume1-snapshot6', 'volume2-snapshot6', 'vm1-backup1', 'volume1-backup1', 'volume2-backup1']
attached:['volume1', 'volume2', 'volume3']
Detached:[]
Deleted:['vm2-snapshot5']
Expunged:[]
Ha:[]
Group:
	vm_snap3:['vm1-snapshot6', 'volume1-snapshot6', 'volume2-snapshot6']---vm1volume1_volume2
	vm_snap1:['vm1-snapshot1', 'volume1-snapshot1', 'volume2-snapshot1', 'volume3-snapshot1']---vm1volume1_volume2_volume3
	vm_backup1:['vm1-backup1', 'volume1-backup1', 'volume2-backup1']---vm1_volume1_volume2
'''