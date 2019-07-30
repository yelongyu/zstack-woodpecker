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
		[TestAction.migrate_volume, 'volume3'],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot5'],
		[TestAction.resize_volume, 'vm2', 5*1024*1024],
		[TestAction.create_vm_snapshot, 'vm2', 'vm2-snapshot9'],
		[TestAction.migrate_vm, 'vm2'],
		[TestAction.create_volume_snapshot, 'volume3', 'volume3-snapshot13'],
		[TestAction.batch_delete_volume_snapshot, ['volume3-snapshot13','vm2-snapshot9',]],
		[TestAction.delete_vm_snapshot, 'vm1-snapshot1'],
])



'''
The final status:
Running:['vm1', 'vm2']
Stopped:[]
Enadbled:['vm1-snapshot5', 'volume1-snapshot5', 'volume2-snapshot5', 'volume3-snapshot5', 'volume4-snapshot9', 'volume5-snapshot9', 'volume6-snapshot9']
attached:['volume1', 'volume2', 'volume3', 'volume4', 'volume5', 'volume6']
Detached:[]
Deleted:['volume3-snapshot13', 'vm2-snapshot9', 'vm1-snapshot1', 'volume1-snapshot1', 'volume2-snapshot1', 'volume3-snapshot1']
Expunged:[]
Ha:[]
Group:
	vm_snap2:['vm1-snapshot5', 'volume1-snapshot5', 'volume2-snapshot5', 'volume3-snapshot5']---vm1volume1_volume2_volume3
'''