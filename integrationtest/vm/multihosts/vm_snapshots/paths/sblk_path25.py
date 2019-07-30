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
		[TestAction.resize_data_volume, 'volume1', 5*1024*1024],
		[TestAction.create_vm_snapshot, 'vm2', 'vm2-snapshot5'],
		[TestAction.stop_vm, 'vm2'],
		[TestAction.use_volume_snapshot, 'vm2-snapshot5'],
		[TestAction.start_vm, 'vm2'],
		[TestAction.create_vm_snapshot, 'vm2', 'vm2-snapshot6'],
		[TestAction.resize_volume, 'vm2', 5*1024*1024],
		[TestAction.create_volume_backup, 'volume2', 'volume2-backup1'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.use_volume_backup, 'volume2-backup1'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.clone_vm, 'vm1', 'vm3'],
		[TestAction.delete_vm_snapshot, 'vm2-snapshot5'],
])



'''
The final status:
Running:['vm2', 'vm1', 'vm3']
Stopped:[]
Enadbled:['vm1-snapshot1', 'volume1-snapshot1', 'volume2-snapshot1', 'volume3-snapshot1', 'vm2-snapshot6', 'volume2-backup1']
attached:['volume1', 'volume2', 'volume3']
Detached:[]
Deleted:['vm2-snapshot5']
Expunged:[]
Ha:[]
Group:
	vm_snap3:['vm2-snapshot6']---vm2
	vm_snap1:['vm1-snapshot1', 'volume1-snapshot1', 'volume2-snapshot1', 'volume3-snapshot1']---vm1volume1_volume2_volume3
'''