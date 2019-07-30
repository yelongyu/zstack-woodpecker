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
		[TestAction.detach_volume, 'volume2'],
		[TestAction.create_vm_snapshot, 'vm2', 'vm2-snapshot5'],
		[TestAction.create_vm_backup, 'vm2', 'vm2-backup1'],
		[TestAction.create_vm_snapshot, 'vm2', 'vm2-snapshot6'],
		[TestAction.clone_vm, 'vm1', 'vm3', 'full'],
		[TestAction.delete_volume, 'volume1'],
		[TestAction.batch_delete_volume_snapshot, ['vm2-snapshot5','vm2-snapshot6',]],
		[TestAction.delete_vm_snapshot, 'vm1-snapshot1'],
])



'''
The final status:
Running:['vm1', 'vm2', 'vm3']
Stopped:[]
Enadbled:['vm2-backup1']
attached:['volume3', 'volume4', 'volume5']
Detached:['volume2']
Deleted:['volume1', 'vm2-snapshot5', 'vm2-snapshot6', 'vm1-snapshot1', 'volume1-snapshot1', 'volume2-snapshot1', 'volume3-snapshot1']
Expunged:[]
Ha:[]
Group:
	vm_backup1:['vm2-backup1']---vm2_
'''