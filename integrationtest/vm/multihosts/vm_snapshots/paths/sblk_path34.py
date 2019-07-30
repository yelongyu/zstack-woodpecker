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
		[TestAction.create_data_vol_template_from_volume, 'volume3', 'volume3-image1'],
		[TestAction.create_vm_snapshot, 'vm2', 'vm2-snapshot5'],
		[TestAction.migrate_vm, 'vm2'],
		[TestAction.create_vm_snapshot, 'vm2', 'vm2-snapshot9'],
		[TestAction.delete_vm_snapshot, 'vm1-snapshot1'],
		[TestAction.create_volume, 'volume7', 'flag=scsi'],
		[TestAction.attach_volume, 'vm1', 'volume7'],
		[TestAction.clone_vm, 'vm1', 'vm3'],
		[TestAction.delete_vm_snapshot, 'vm2-snapshot5'],
])



'''
The final status:
Running:['vm1', 'vm2', 'vm3']
Stopped:[]
Enadbled:['vm2-snapshot9', 'volume4-snapshot9', 'volume5-snapshot9', 'volume6-snapshot9', 'volume3-image1']
attached:['volume1', 'volume2', 'volume3', 'volume4', 'volume5', 'volume6', 'volume7']
Detached:[]
Deleted:['vm1-snapshot1', 'volume1-snapshot1', 'volume2-snapshot1', 'volume3-snapshot1', 'vm2-snapshot5', 'volume4-snapshot5', 'volume5-snapshot5', 'volume6-snapshot5']
Expunged:[]
Ha:[]
Group:
	vm_snap3:['vm2-snapshot9', 'volume4-snapshot9', 'volume5-snapshot9', 'volume6-snapshot9']---vm2volume4_volume5_volume6
'''