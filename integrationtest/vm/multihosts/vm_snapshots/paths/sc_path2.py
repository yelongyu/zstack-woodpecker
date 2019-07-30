import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", path_list=[
		[TestAction.create_vm, 'vm1', 'flag=sblk'],
		[TestAction.create_volume, 'volume1', 'flag=ceph,scsi'],
		[TestAction.create_volume, 'volume2', 'flag=sblk,scsi'],
		[TestAction.create_volume, 'volume3', 'flag=ceph,scsi'],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot1'],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot2'],
		[TestAction.create_volume_snapshot, 'vm1-root', 'vm1-root-snapshot3'],
		[TestAction.create_volume_snapshot, 'volume1', 'volume1-snapshot4'],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot5'],
		[TestAction.create_volume_snapshot, 'volume2', 'volume2-snapshot6'],
		[TestAction.create_volume_snapshot, 'volume2', 'volume2-snapshot7'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.use_volume_snapshot, 'vm1-root-snapshot3'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.use_volume_snapshot, 'volume2-snapshot6'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.use_vm_snapshot, 'vm1-snapshot1'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.resize_data_volume, 'volume1', 5*1024*1024],
		[TestAction.delete_volume_snapshot, 'vm1-root-snapshot3'],
		[TestAction.delete_volume_snapshot, 'vm1-snapshot1'],
		[TestAction.delete_volume_snapshot, 'volume1-snapshot4'],
])



'''
The final status:
Running:['vm1']
Stopped:[]
Enadbled:['vm1-snapshot2', 'vm1-snapshot5', 'volume2-snapshot6', 'volume2-snapshot7']
attached:[]
Detached:['volume1', 'volume2', 'volume3']
Deleted:['vm1-root-snapshot3', 'vm1-snapshot1', 'volume1-snapshot4']
Expunged:[]
Ha:[]
Group:
	vm_snap2:['vm1-snapshot2']---vm1
	vm_snap3:['vm1-snapshot5']---vm1
'''