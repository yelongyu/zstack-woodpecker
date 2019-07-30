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
		[TestAction.reinit_vm, 'vm1'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.detach_volume, 'volume3'],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot5'],
		[TestAction.delete_vm_snapshot, 'vm1-snapshot1'],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot8'],
		[TestAction.create_volume_backup, 'vm1-root', 'vm1-root-backup1'],
		[TestAction.delete_volume_snapshot, 'volume1-snapshot5'],
		[TestAction.clone_vm, 'vm1', 'vm2', 'full'],
		[TestAction.delete_vm_snapshot, 'vm1-snapshot5'],
])



'''
The final status:
Running:['vm1', 'vm2']
Stopped:[]
Enadbled:['vm1-snapshot5', 'volume2-snapshot5', 'vm1-root-backup1']
attached:['volume1', 'volume2', 'volume4', 'volume5']
Detached:['volume3']
Deleted:['vm1-snapshot1', 'volume1-snapshot1', 'volume2-snapshot1', 'volume3-snapshot1', 'volume1-snapshot5', 'vm1-snapshot8', 'volume1-snapshot8', 'volume2-snapshot8']
Expunged:[]
Ha:[]
Group:
'''