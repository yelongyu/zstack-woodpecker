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
		[TestAction.create_image_from_volume, 'vm1', 'vm1-image1'],
		[TestAction.create_volume_snapshot, 'volume1', 'volume1-snapshot5'],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot6'],
		[TestAction.create_image_from_volume, 'vm1', 'vm1-image2'],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot10'],
		[TestAction.create_image_from_volume, 'vm1', 'vm1-image3'],
		[TestAction.create_volume_backup, 'volume3', 'volume3-backup1'],
		[TestAction.clone_vm, 'vm1', 'vm2', 'full'],
		[TestAction.delete_vm_snapshot, 'vm1-snapshot1'],
])



'''
The final status:
Running:['vm1', 'vm2']
Stopped:[]
Enadbled:['volume1-snapshot5', 'vm1-snapshot6', 'volume1-snapshot6', 'volume2-snapshot6', 'volume3-snapshot6', 'vm1-snapshot10', 'volume1-snapshot10', 'volume2-snapshot10', 'volume3-snapshot10', 'volume3-backup1', 'vm1-image1', 'vm1-image2', 'vm1-image3']
attached:['volume1', 'volume2', 'volume3', 'volume4', 'volume5', 'volume6']
Detached:[]
Deleted:['vm1-snapshot1', 'volume1-snapshot1', 'volume2-snapshot1', 'volume3-snapshot1']
Expunged:[]
Ha:[]
Group:
	vm_snap2:['vm1-snapshot6', 'volume1-snapshot6', 'volume2-snapshot6', 'volume3-snapshot6']---vm1volume1_volume2_volume3
	vm_snap3:['vm1-snapshot10', 'volume1-snapshot10', 'volume2-snapshot10', 'volume3-snapshot10']---vm1volume1_volume2_volume3
'''