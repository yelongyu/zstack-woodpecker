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
		[TestAction.change_vm_image, 'vm1'],
		[TestAction.create_data_vol_template_from_volume, 'volume3', 'volume3-image1'],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot5'],
		[TestAction.change_vm_image, 'vm1'],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot9'],
		[TestAction.delete_vm_snapshot, 'vm1-snapshot1'],
		[TestAction.delete_volume, 'volume2'],
		[TestAction.clone_vm, 'vm1', 'vm2', 'full'],
		[TestAction.delete_vm_snapshot, 'vm1-snapshot5'],
])



'''
The final status:
Running:['vm2']
Stopped:['vm1']
Enadbled:['vm1-snapshot9', 'volume1-snapshot9', 'volume2-snapshot9', 'volume3-snapshot9', 'volume3-image1']
attached:['volume1', 'volume3', 'volume4', 'volume5']
Detached:[]
Deleted:['volume2', 'vm1-snapshot1', 'volume1-snapshot1', 'volume2-snapshot1', 'volume3-snapshot1', 'vm1-snapshot5', 'volume1-snapshot5', 'volume2-snapshot5', 'volume3-snapshot5']
Expunged:[]
Ha:[]
Group:
	vm_snap3:['vm1-snapshot9', 'volume1-snapshot9', 'volume2-snapshot9', 'volume3-snapshot9']---vm1volume1_volume2_volume3
'''