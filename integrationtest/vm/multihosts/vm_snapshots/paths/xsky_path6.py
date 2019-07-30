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
		[TestAction.stop_vm, 'vm1'],
		[TestAction.use_volume_snapshot, 'vm1-snapshot1'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.create_data_vol_template_from_volume, 'volume3', 'volume3-image1'],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot5'],
		[TestAction.clone_vm, 'vm1', 'vm2'],
		[TestAction.create_vm_snapshot, 'vm2', 'vm2-snapshot9'],
		[TestAction.create_volume_backup, 'vm2-root', 'vm2-root-backup1'],
		[TestAction.create_volume_backup, 'volume1', 'volume1-backup2'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.use_volume_backup, 'volume1-backup2'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.create_vm_backup, 'vm2', 'vm2-backup3'],
		[TestAction.delete_vm_snapshot, 'vm2-snapshot9'],
])



'''
The final status:
Running:['vm2', 'vm1']
Stopped:[]
Enadbled:['vm1-snapshot1', 'volume1-snapshot1', 'volume2-snapshot1', 'volume3-snapshot1', 'vm1-snapshot5', 'volume1-snapshot5', 'volume2-snapshot5', 'volume3-snapshot5', 'vm2-root-backup1', 'volume1-backup2', 'vm2-backup3', 'volume3-image1']
attached:['volume1', 'volume2', 'volume3']
Detached:[]
Deleted:['vm2-snapshot9']
Expunged:[]
Ha:[]
Group:
	vm_snap2:['vm1-snapshot5', 'volume1-snapshot5', 'volume2-snapshot5', 'volume3-snapshot5']---vm1volume1_volume2_volume3
	vm_snap1:['vm1-snapshot1', 'volume1-snapshot1', 'volume2-snapshot1', 'volume3-snapshot1']---vm1volume1_volume2_volume3
	vm_backup1:['vm2-backup3']---vm2_
'''