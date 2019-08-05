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
		[TestAction.create_volume_backup, 'clone@volume2', 'clone@volume2-backup1'],
		[TestAction.stop_vm, 'vm2'],
		[TestAction.use_volume_backup, 'clone@volume2-backup1'],
		[TestAction.start_vm, 'vm2'],
		[TestAction.create_vm_snapshot, 'vm2', 'vm2-snapshot5'],
		[TestAction.create_image_from_volume, 'vm1', 'vm1-image1'],
		[TestAction.create_vm_snapshot, 'vm2', 'vm2-snapshot9'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.use_volume_snapshot, 'vm1-snapshot1'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.create_volume_snapshot, 'clone@volume3', 'clone@volume3-snapshot13'],
		[TestAction.delete_vm_snapshot, 'vm1-snapshot1'],
		[TestAction.delete_vm_snapshot, 'vm2-snapshot5'],
])



'''
The final status:
Running:['vm2', 'vm1']
Stopped:[]
Enadbled:['vm2-snapshot9', 'clone@volume1-snapshot9', 'clone@volume2-snapshot9', 'clone@volume3-snapshot9', 'clone@volume3-snapshot13', 'clone@volume2-backup1', 'vm1-image1']
attached:['volume1', 'volume2', 'volume3', 'clone@volume1', 'clone@volume2', 'clone@volume3']
Detached:[]
Deleted:['vm1-snapshot1', 'volume1-snapshot1', 'volume2-snapshot1', 'volume3-snapshot1', 'vm2-snapshot5', 'clone@volume1-snapshot5', 'clone@volume2-snapshot5', 'clone@volume3-snapshot5']
Expunged:[]
Ha:[]
Group:
	vm_snap3:['vm2-snapshot9', 'clone@volume1-snapshot9', 'clone@volume2-snapshot9', 'clone@volume3-snapshot9']---vm2clone@volume1_clone@volume2_clone@volume3
'''