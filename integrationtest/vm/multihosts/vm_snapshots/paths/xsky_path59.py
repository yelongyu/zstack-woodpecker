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
		[TestAction.reboot_vm, 'vm1'],
		[TestAction.migrate_volume, 'volume2'],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot5'],
		[TestAction.clone_vm, 'vm1', 'vm2', 'full'],
		[TestAction.create_vm_snapshot, 'vm2', 'vm2-snapshot9'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.ps_migrate_vm, 'vm1'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.delete_volume, 'volume5'],
		[TestAction.create_vm_backup, 'vm2', 'vm2-backup1'],
		[TestAction.delete_vm_snapshot, 'vm2-snapshot9'],
])



'''
The final status:
Running:['vm2', 'vm1']
Stopped:[]
Enadbled:['vm1-snapshot1', 'volume1-snapshot1', 'volume2-snapshot1', 'volume3-snapshot1', 'vm1-snapshot5', 'volume1-snapshot5', 'volume2-snapshot5', 'volume3-snapshot5', 'vm2-backup1', 'volume4-backup1', 'volume6-backup1']
attached:['volume1', 'volume2', 'volume3', 'volume4', 'volume6']
Detached:[]
Deleted:['volume5', 'vm2-snapshot9', 'volume4-snapshot9', 'volume5-snapshot9', 'volume6-snapshot9']
Expunged:[]
Ha:[]
Group:
	vm_snap2:['vm1-snapshot5', 'volume1-snapshot5', 'volume2-snapshot5', 'volume3-snapshot5']---vm1volume1_volume2_volume3
	vm_snap1:['vm1-snapshot1', 'volume1-snapshot1', 'volume2-snapshot1', 'volume3-snapshot1']---vm1volume1_volume2_volume3
	vm_backup1:['vm2-backup1', 'volume4-backup1', 'volume6-backup1']---vm2_volume4_volume6
'''