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
		[TestAction.detach_volume, 'volume4'],
		[TestAction.create_vm_snapshot, 'vm2', 'vm2-snapshot5'],
		[TestAction.clone_vm, 'vm1', 'vm3', 'full'],
		[TestAction.create_vm_snapshot, 'vm3', 'vm3-snapshot8'],
		[TestAction.batch_delete_volume_snapshot, ['volume5-snapshot5','volume8-snapshot8',]],
		[TestAction.delete_volume, 'volume8'],
		[TestAction.clone_vm, 'vm1', 'vm4', 'full'],
		[TestAction.delete_vm_snapshot, 'vm1-snapshot1'],
])



'''
The final status:
Running:['vm1', 'vm2', 'vm3', 'vm4']
Stopped:[]
Enadbled:['vm2-snapshot5', 'volume6-snapshot5', 'vm3-snapshot8', 'volume7-snapshot8', 'volume9-snapshot8']
attached:['volume1', 'volume2', 'volume3', 'volume5', 'volume6', 'volume7', 'volume9', 'volume10', 'volume11', 'volume12']
Detached:['volume4']
Deleted:['volume8', 'volume5-snapshot5', 'volume8-snapshot8', 'vm1-snapshot1', 'volume1-snapshot1', 'volume2-snapshot1', 'volume3-snapshot1']
Expunged:[]
Ha:[]
Group:
'''