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
		[TestAction.delete_volume, 'volume4'],
		[TestAction.create_vm_snapshot, 'vm2', 'vm2-snapshot5'],
		[TestAction.clone_vm, 'vm1', 'vm3', 'full'],
		[TestAction.create_vm_snapshot, 'vm2', 'vm2-snapshot8'],
		[TestAction.clone_vm, 'vm1', 'vm4'],
		[TestAction.delete_volume, 'volume1'],
		[TestAction.stop_vm, 'vm2'],
		[TestAction.use_volume_snapshot, 'vm2-snapshot8'],
		[TestAction.start_vm, 'vm2'],
		[TestAction.delete_vm_snapshot, 'vm1-snapshot1'],
])



'''
The final status:
Running:['vm1', 'vm3', 'vm4', 'vm2']
Stopped:[]
Enadbled:['vm2-snapshot5', 'volume5-snapshot5', 'volume6-snapshot5', 'vm2-snapshot8', 'volume5-snapshot8', 'volume6-snapshot8']
attached:['volume2', 'volume3', 'volume5', 'volume6', 'volume7', 'volume8', 'volume9']
Detached:[]
Deleted:['volume4', 'volume1', 'vm1-snapshot1', 'volume1-snapshot1', 'volume2-snapshot1', 'volume3-snapshot1']
Expunged:[]
Ha:[]
Group:
	vm_snap2:['vm2-snapshot5', 'volume5-snapshot5', 'volume6-snapshot5']---vm2volume5_volume6
	vm_snap3:['vm2-snapshot8', 'volume5-snapshot8', 'volume6-snapshot8']---vm2volume5_volume6
'''