import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", path_list=[
		[TestAction.create_vm, 'vm1', 'flag=ceph'],
		[TestAction.create_volume, 'volume1', 'flag=ceph,scsi'],
		[TestAction.attach_volume, 'vm1', 'volume1'],
		[TestAction.create_volume, 'volume2', 'flag=ceph,scsi'],
		[TestAction.attach_volume, 'vm1', 'volume2'],
		[TestAction.create_volume, 'volume3', 'flag=ceph,scsi'],
		[TestAction.attach_volume, 'vm1', 'volume3'],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot1'],
		[TestAction.create_volume_backup, 'vm1-root', 'vm1-root-backup1'],
		[TestAction.create_data_vol_template_from_volume, 'volume1', 'volume1-image1'],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot5'],
		[TestAction.create_image_from_volume, 'vm1', 'vm1-image2'],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot9'],
		[TestAction.batch_delete_volume_snapshot, ['volume1-snapshot9','vm1-snapshot9',]],
		[TestAction.create_data_vol_template_from_volume, 'volume1', 'volume1-image3'],
		[TestAction.create_image_from_volume, 'vm1', 'vm1-image4'],
		[TestAction.delete_vm_snapshot, 'vm1-snapshot1'],
])



'''
The final status:
Running:['vm1']
Stopped:[]
Enadbled:['vm1-snapshot5', 'volume1-snapshot5', 'volume2-snapshot5', 'volume3-snapshot5', 'volume2-snapshot9', 'volume3-snapshot9', 'vm1-root-backup1', 'volume1-image1', 'vm1-image2', 'volume1-image3', 'vm1-image4']
attached:['volume1', 'volume2', 'volume3']
Detached:[]
Deleted:['volume1-snapshot9', 'vm1-snapshot9', 'vm1-snapshot1', 'volume1-snapshot1', 'volume2-snapshot1', 'volume3-snapshot1']
Expunged:[]
Ha:[]
Group:
	vm_snap2:['vm1-snapshot5', 'volume1-snapshot5', 'volume2-snapshot5', 'volume3-snapshot5']---vm1@volume1_volume2_volume3
'''