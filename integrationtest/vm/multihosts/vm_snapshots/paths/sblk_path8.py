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
		[TestAction.create_volume_backup, 'volume2', 'volume2-backup1'],
		[TestAction.create_vm_snapshot, 'vm2', 'vm2-snapshot5'],
		[TestAction.create_volume_snapshot, 'vm2-root', 'vm2-root-snapshot9'],
		[TestAction.create_vm_snapshot, 'vm2', 'vm2-snapshot10'],
		[TestAction.create_volume_backup, 'vm1-root', 'vm1-root-backup2'],
		[TestAction.delete_volume, 'volume1'],
		[TestAction.create_volume_backup, 'vm1-root', 'vm1-root-backup3'],
		[TestAction.delete_vm_snapshot, 'vm2-snapshot5'],
])



'''
The final status:
Running:['vm1', 'vm2']
Stopped:[]
Enadbled:['vm1-snapshot1', 'volume1-snapshot1', 'volume2-snapshot1', 'volume3-snapshot1', 'vm2-root-snapshot9', 'vm2-snapshot10', 'volume4-snapshot10', 'volume5-snapshot10', 'volume6-snapshot10', 'volume2-backup1', 'vm1-root-backup2', 'vm1-root-backup3']
attached:['volume2', 'volume3', 'volume4', 'volume5', 'volume6']
Detached:[]
Deleted:['volume1', 'vm2-snapshot5', 'volume4-snapshot5', 'volume5-snapshot5', 'volume6-snapshot5']
Expunged:[]
Ha:[]
Group:
	vm_snap3:['vm2-snapshot10', 'volume4-snapshot10', 'volume5-snapshot10', 'volume6-snapshot10']---vm2volume4_volume5_volume6
	vm_snap1:['vm1-snapshot1', 'volume1-snapshot1', 'volume2-snapshot1', 'volume3-snapshot1']---vm1volume1_volume2_volume3
'''