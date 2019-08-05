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
		[TestAction.stop_vm, 'vm1'],
		[TestAction.use_volume_snapshot, 'volume3-snapshot1'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot5'],
		[TestAction.delete_vm_snapshot, 'vm1-snapshot1'],
		[TestAction.create_vm_snapshot, 'vm2', 'vm2-snapshot9'],
		[TestAction.reboot_vm, 'vm2'],
		[TestAction.create_volume_backup, 'volume2', 'volume2-backup1'],
		[TestAction.create_vm_backup, 'vm1', 'vm1-backup2'],
		[TestAction.delete_vm_snapshot, 'vm2-snapshot9'],
])



'''
The final status:
Running:['vm2', 'vm1']
Stopped:[]
Enadbled:['vm1-snapshot5', 'volume1-snapshot5', 'volume2-snapshot5', 'volume3-snapshot5', 'volume2-backup1', 'vm1-backup2', 'volume1-backup2', 'volume2-backup2', 'volume3-backup2']
attached:['volume1', 'volume2', 'volume3', 'clone@volume1', 'clone@volume2', 'clone@volume3']
Detached:[]
Deleted:['vm1-snapshot1', 'volume1-snapshot1', 'volume2-snapshot1', 'volume3-snapshot1', 'vm2-snapshot9', 'clone@volume1-snapshot9', 'clone@volume2-snapshot9', 'clone@volume3-snapshot9']
Expunged:[]
Ha:[]
Group:
	vm_backup1:['vm1-backup2', 'volume1-backup2', 'volume2-backup2', 'volume3-backup2']---vm1@volume1_volume2_volume3
'''