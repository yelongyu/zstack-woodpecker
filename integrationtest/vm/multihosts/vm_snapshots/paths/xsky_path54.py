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
		[TestAction.clone_vm, 'vm1', 'vm2'],
		[TestAction.create_volume, 'volume4', 'flag=scsi'],
		[TestAction.attach_volume, 'vm2', 'volume4'],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot5'],
		[TestAction.delete_vm_snapshot, 'vm1-snapshot1'],
		[TestAction.create_vm_snapshot, 'vm2', 'vm2-snapshot9'],
		[TestAction.create_vm_backup, 'vm2', 'vm2-backup1'],
		[TestAction.create_data_vol_template_from_volume, 'volume3', 'volume3-image1'],
		[TestAction.create_image_from_volume, 'vm2', 'vm2-image2'],
		[TestAction.delete_vm_snapshot, 'vm2-snapshot9'],
])



'''
The final status:
Running:['vm1', 'vm2']
Stopped:[]
Enadbled:['vm1-snapshot5', 'volume1-snapshot5', 'volume2-snapshot5', 'volume3-snapshot5', 'vm2-backup1', 'volume4-backup1', 'volume3-image1', 'vm2-image2']
attached:['volume1', 'volume2', 'volume3', 'volume4']
Detached:[]
Deleted:['vm1-snapshot1', 'volume1-snapshot1', 'volume2-snapshot1', 'volume3-snapshot1', 'vm2-snapshot9', 'volume4-snapshot9']
Expunged:[]
Ha:[]
Group:
	vm_backup1:['vm2-backup1', 'volume4-backup1']---vm2_volume4
'''