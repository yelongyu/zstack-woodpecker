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
		[TestAction.create_volume_backup, 'vm1-root', 'vm1-root-backup1'],
		[TestAction.delete_volume, 'volume1'],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot5'],
		[TestAction.reboot_vm, 'vm1'],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot8'],
		[TestAction.create_vm_backup, 'vm1', 'vm1-backup2'],
		[TestAction.delete_volume, 'volume3'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.ps_migrate_vm, 'vm1'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.delete_vm_snapshot, 'vm1-snapshot1'],
])



'''
The final status:
Running:['vm1']
Stopped:[]
Enadbled:['vm1-snapshot5', 'volume2-snapshot5', 'volume3-snapshot5', 'vm1-snapshot8', 'volume2-snapshot8', 'volume3-snapshot8', 'vm1-root-backup1', 'vm1-backup2', 'volume2-backup2', 'volume3-backup2']
attached:['volume2']
Detached:[]
Deleted:['volume1', 'volume3', 'vm1-snapshot1', 'volume1-snapshot1', 'volume2-snapshot1', 'volume3-snapshot1']
Expunged:[]
Ha:[]
Group:
	vm_snap2:['vm1-snapshot5', 'volume2-snapshot5', 'volume3-snapshot5']---vm1volume2_volume3
	vm_snap3:['vm1-snapshot8', 'volume2-snapshot8', 'volume3-snapshot8']---vm1volume2_volume3
	vm_backup1:['vm1-backup2', 'volume2-backup2', 'volume3-backup2']---vm1_volume2_volume3
'''