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
		[TestAction.create_volume_snapshot, 'vm1-root', 'vm1-root-snapshot1'],
		[TestAction.create_volume_snapshot, 'volume1', 'volume1-snapshot2'],
		[TestAction.create_volume_snapshot, 'volume3', 'volume3-snapshot3'],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot4'],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot8'],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot12'],
		[TestAction.create_volume_snapshot, 'vm1-root', 'vm1-root-snapshot16'],
		[TestAction.create_volume_snapshot, 'volume1', 'volume1-snapshot17'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.use_volume_snapshot, 'vm1-snapshot8'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.use_volume_snapshot, 'vm1-root-snapshot1'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.resize_data_volume, 'volume1', 5*1024*1024],
		[TestAction.batch_delete_snapshots, ['volume2-snapshot4','volume3-snapshot8',]],
		[TestAction.delete_volume_snapshot, 'vm1-snapshot8'],
		TestAction.batch_delete_snapshots, ['vm1-snapshot4','volume2-snapshot8',],
])



'''
The final status:
Running:['vm1']
Stopped:[]
Enadbled:['vm1-root-snapshot1', 'volume1-snapshot2', 'volume3-snapshot3', 'volume1-snapshot4', 'volume3-snapshot4', 'volume1-snapshot8', 'vm1-snapshot12', 'volume1-snapshot12', 'volume2-snapshot12', 'volume3-snapshot12', 'vm1-root-snapshot16', 'volume1-snapshot17']
attached:['volume1', 'volume2', 'volume3']
Detached:[]
Deleted:['volume2-snapshot4', 'volume3-snapshot8', 'vm1-snapshot8', 'vm1-snapshot4', 'volume2-snapshot8']
Expunged:[]
Ha:[]
Group:
	vm_snap3:['vm1-snapshot12', 'volume1-snapshot12', 'volume2-snapshot12', 'volume3-snapshot12']---vm1volume1_volume2_volume3
'''
