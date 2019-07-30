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
		[TestAction.create_volume_backup, 'volume2', 'volume2-backup2'],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot5'],
		[TestAction.clone_vm, 'vm1', 'vm2', 'full'],
		[TestAction.create_vm_snapshot, 'vm2', 'vm2-snapshot9'],
		[TestAction.stop_vm, 'vm2'],
		[TestAction.change_vm_image, 'vm2'],
		[TestAction.delete_volume_snapshot, 'vm2-snapshot9'],
		[TestAction.start_vm, 'vm2'],
		[TestAction.create_vm_backup, 'vm2', 'vm2-backup3'],
		[TestAction.stop_vm, 'vm2'],
		[TestAction.delete_vm_snapshot, 'vm1-snapshot1'],
])



'''
The final status:
Running:['vm1']
Stopped:['vm2']
Enadbled:['vm1-snapshot5', 'volume1-snapshot5', 'volume2-snapshot5', 'volume3-snapshot5', 'volume4-snapshot9', 'volume5-snapshot9', 'volume6-snapshot9', 'vm1-root-backup1', 'volume2-backup2', 'vm2-backup3', 'volume4-backup3', 'volume5-backup3', 'volume6-backup3']
attached:['volume1', 'volume2', 'volume3', 'volume4', 'volume5', 'volume6']
Detached:[]
Deleted:['vm2-snapshot9', 'vm1-snapshot1', 'volume1-snapshot1', 'volume2-snapshot1', 'volume3-snapshot1']
Expunged:[]
Ha:[]
Group:
	vm_snap2:['vm1-snapshot5', 'volume1-snapshot5', 'volume2-snapshot5', 'volume3-snapshot5']---vm1volume1_volume2_volume3
	vm_backup1:['vm2-backup3', 'volume4-backup3', 'volume5-backup3', 'volume6-backup3']---vm2_volume4_volume5_volume6
'''