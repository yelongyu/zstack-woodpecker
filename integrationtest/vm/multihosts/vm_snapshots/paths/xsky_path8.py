import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", checking_point=8, path_list=[
		[TestAction.create_vm, 'vm1', ],
		[TestAction.create_volume, 'volume1', 'flag=scsi'],
		[TestAction.attach_volume, 'vm1', 'volume1'],
		[TestAction.create_volume, 'volume2', 'flag=scsi'],
		[TestAction.attach_volume, 'vm1', 'volume2'],
		[TestAction.create_volume, 'volume3', 'flag=scsi'],
		[TestAction.attach_volume, 'vm1', 'volume3'],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot1'],
		[TestAction.clone_vm, 'vm1', 'vm2'],
		[TestAction.create_volume_backup, 'volume3', 'volume3-backup1'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.use_volume_backup, 'volume3-backup1'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.create_vm_snapshot, 'vm2', 'vm2-snapshot5'],
		[TestAction.delete_vm_snapshot, 'vm1-snapshot1'],
		[TestAction.create_vm_snapshot, 'vm2', 'vm2-snapshot6'],
		[TestAction.clone_vm, 'vm2', 'vm3', 'full'],
		[TestAction.delete_volume_snapshot, 'vm2-snapshot5'],
		[TestAction.stop_vm, 'vm2'],
		[TestAction.change_vm_image, 'vm2'],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot7'],
		[TestAction.delete_vm_snapshot, 'vm1-snapshot7'],
])



'''
The final status:
Running:['vm1', 'vm3']
Stopped:['vm2']
Enadbled:['vm2-snapshot6', 'volume3-backup1']
attached:['volume1', 'volume2', 'volume3']
Detached:[]
Deleted:['vm1-snapshot1', 'volume1-snapshot1', 'volume2-snapshot1', 'volume3-snapshot1', 'vm2-snapshot5', 'vm1-snapshot7', 'volume1-snapshot7', 'volume2-snapshot7', 'volume3-snapshot7']
Expunged:[]
Ha:[]
Group:
'''
