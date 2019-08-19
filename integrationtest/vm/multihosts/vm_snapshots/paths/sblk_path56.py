import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", checking_point=8, path_list=[
		[TestAction.create_vm, 'vm1', ],
		[TestAction.create_volume, 'volume1', 'flag=scsi'],
		[TestAction.attach_volume, 'vm1', 'volume1'],
		[TestAction.create_volume, 'volume2', 'flag=scsi'],
		[TestAction.attach_volume, 'vm1', 'volume2'],
		[TestAction.create_volume, 'volume3', 'flag=scsi'],
		[TestAction.attach_volume, 'vm1', 'volume3'],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot1'],
		[TestAction.clone_vm, 'vm1', 'vm2'],
		[TestAction.detach_volume, 'volume2'],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot5'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.change_vm_image, 'vm1'],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot8'],
		[TestAction.create_image_from_volume, 'vm1', 'vm1-image1'],
		[TestAction.attach_volume, 'vm2', 'volume2'],
		[TestAction.create_volume_backup, 'volume2', 'volume2-backup1'],
		[TestAction.stop_vm, 'vm2'],
		[TestAction.use_volume_backup, 'volume2-backup1'],
		[TestAction.start_vm, 'vm2'],
		[TestAction.detach_volume, 'volume2'],
		[TestAction.change_vm_image, 'vm1'],
		[TestAction.delete_vm_snapshot, 'vm1-snapshot1'],
])



'''
The final status:
Running:['vm2']
Stopped:['vm1']
Enadbled:['vm1-snapshot5', 'volume1-snapshot5', 'volume3-snapshot5', 'vm1-snapshot8', 'volume1-snapshot8', 'volume3-snapshot8', 'volume2-backup1', 'vm1-image1']
attached:['volume1', 'volume3']
Detached:['volume2']
Deleted:['vm1-snapshot1', 'volume1-snapshot1', 'volume2-snapshot1', 'volume3-snapshot1']
Expunged:[]
Ha:[]
Group:
	vm_snap2:['vm1-snapshot5', 'volume1-snapshot5', 'volume3-snapshot5']---vm1volume1_volume3
	vm_snap3:['vm1-snapshot8', 'volume1-snapshot8', 'volume3-snapshot8']---vm1volume1_volume3
'''
