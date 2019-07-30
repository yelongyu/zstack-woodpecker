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
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot5'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.reinit_vm, 'vm1'],
		[TestAction.create_vm_snapshot, 'vm2', 'vm2-snapshot9'],
		[TestAction.create_volume_snapshot, 'vm2-root', 'vm2-root-snapshot12'],
		[TestAction.create_volume_backup, 'volume4', 'volume4-backup1'],
		[TestAction.stop_vm, 'vm2'],
		[TestAction.use_volume_backup, 'volume4-backup1'],
		[TestAction.start_vm, 'vm2'],
		[TestAction.create_image_from_volume, 'vm2', 'vm2-image1'],
		[TestAction.delete_vm_snapshot, 'vm1-snapshot1'],
])



'''
The final status:
Running:['vm2']
Stopped:['vm1']
Enadbled:['vm1-snapshot5', 'volume1-snapshot5', 'volume2-snapshot5', 'volume3-snapshot5', 'vm2-snapshot9', 'volume4-snapshot9', 'volume6-snapshot9', 'vm2-root-snapshot12', 'volume4-backup1', 'vm2-image1']
attached:['volume1', 'volume2', 'volume3', 'volume4', 'volume6']
Detached:['volume5']
Deleted:['vm1-snapshot1', 'volume1-snapshot1', 'volume2-snapshot1', 'volume3-snapshot1']
Expunged:[]
Ha:[]
Group:
	vm_snap2:['vm1-snapshot5', 'volume1-snapshot5', 'volume2-snapshot5', 'volume3-snapshot5']---vm1volume1_volume2_volume3
	vm_snap3:['vm2-snapshot9', 'volume4-snapshot9', 'volume6-snapshot9']---vm2volume4_volume6
'''