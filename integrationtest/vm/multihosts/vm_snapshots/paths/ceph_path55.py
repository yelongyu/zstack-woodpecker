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
		[TestAction.detach_volume, 'volume3'],
		[TestAction.create_vm_snapshot, 'vm2', 'vm2-snapshot5'],
		[TestAction.clone_vm, 'vm2', 'vm3', 'full'],
		[TestAction.create_vm_snapshot, 'vm2', 'vm2-snapshot9'],
		[TestAction.batch_delete_volume_snapshot, ['volume3-snapshot1','vm2-snapshot5',]],
		[TestAction.delete_volume, 'clone@volume1'],
		[TestAction.clone_vm, 'vm1', 'vm4', 'full'],
		[TestAction.delete_vm_snapshot, 'vm2-snapshot9'],
])



'''
The final status:
Running:['vm1', 'vm2', 'vm3', 'vm4']
Stopped:[]
Enadbled:['vm1-snapshot1', 'volume1-snapshot1', 'volume2-snapshot1', 'clone@volume1-snapshot5', 'clone@volume2-snapshot5', 'clone@volume3-snapshot5']
attached:['volume1', 'volume2', 'clone@volume2', 'clone@volume3', 'clone@clone@volume1', 'clone@clone@volume2', 'clone@clone@volume3', 'clone@volume1', 'clone@volume2']
Detached:['volume3']
Deleted:['clone@volume1', 'volume3-snapshot1', 'vm2-snapshot5', 'vm2-snapshot9', 'clone@volume1-snapshot9', 'clone@volume2-snapshot9', 'clone@volume3-snapshot9']
Expunged:[]
Ha:[]
Group:
'''