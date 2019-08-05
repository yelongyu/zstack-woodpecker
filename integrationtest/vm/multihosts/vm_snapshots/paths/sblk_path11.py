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
		[TestAction.resize_data_volume, 'volume3', 5*1024*1024],
		[TestAction.create_vm_snapshot, 'vm2', 'vm2-snapshot5'],
		[TestAction.create_vm_backup, 'vm2', 'vm2-backup1'],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot9'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.ps_migrate_vm, 'vm1'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.stop_vm, 'vm2'],
		[TestAction.use_volume_snapshot, 'clone@volume3-snapshot5'],
		[TestAction.start_vm, 'vm2'],
		[TestAction.resize_volume, 'vm1', 5*1024*1024],
		[TestAction.delete_vm_snapshot, 'vm1-snapshot1'],
])



'''
The final status:
Running:['vm1', 'vm2']
Stopped:[]
Enadbled:['vm2-snapshot5', 'clone@volume1-snapshot5', 'clone@volume2-snapshot5', 'clone@volume3-snapshot5', 'vm1-snapshot9', 'volume1-snapshot9', 'volume2-snapshot9', 'volume3-snapshot9', 'vm2-backup1', 'clone@volume1-backup1', 'clone@volume2-backup1', 'clone@volume3-backup1']
attached:['volume1', 'volume2', 'volume3', 'clone@volume1', 'clone@volume2', 'clone@volume3']
Detached:[]
Deleted:['vm1-snapshot1', 'volume1-snapshot1', 'volume2-snapshot1', 'volume3-snapshot1']
Expunged:[]
Ha:[]
Group:
	vm_snap2:['vm2-snapshot5', 'clone@volume1-snapshot5', 'clone@volume2-snapshot5', 'clone@volume3-snapshot5']---vm2clone@volume1_clone@volume2_clone@volume3
	vm_snap3:['vm1-snapshot9', 'volume1-snapshot9', 'volume2-snapshot9', 'volume3-snapshot9']---vm1volume1_volume2_volume3
	vm_backup1:['vm2-backup1', 'clone@volume1-backup1', 'clone@volume2-backup1', 'clone@volume3-backup1']---vm2_clone@volume1_clone@volume2_clone@volume3
'''