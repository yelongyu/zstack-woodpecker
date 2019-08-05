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
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot5'],
		[TestAction.create_vm_backup, 'vm2', 'vm2-backup1'],
		[TestAction.create_vm_snapshot, 'vm2', 'vm2-snapshot8'],
		[TestAction.clone_vm, 'vm2', 'vm3', 'full'],
		[TestAction.delete_volume, 'volume1'],
		[TestAction.batch_delete_volume_snapshot, ['vm1-snapshot5','volume1-snapshot5',]],
		[TestAction.delete_vm_snapshot, 'vm1-snapshot1'],
])



'''
The final status:
Running:['vm1', 'vm2', 'vm3']
Stopped:[]
Enadbled:['volume3-snapshot5', 'vm2-snapshot8', 'vm2-backup1']
attached:['volume3']
Detached:['volume2']
Deleted:['volume1', 'vm1-snapshot5', 'volume1-snapshot5', 'vm1-snapshot1', 'volume1-snapshot1', 'volume2-snapshot1', 'volume3-snapshot1']
Expunged:[]
Ha:[]
Group:
	vm_snap3:['vm2-snapshot8']---vm2@
	vm_backup1:['vm2-backup1']---vm2@
'''