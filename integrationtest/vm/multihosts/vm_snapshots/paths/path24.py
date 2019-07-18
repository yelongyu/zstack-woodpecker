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
		[TestAction.create_volume_snapshot, 'volume1', 'volume1-snapshot1'],
		[TestAction.create_volume_snapshot, 'volume2', 'volume2-snapshot2'],
		[TestAction.create_volume_snapshot, 'vm1-root', 'vm1-root-snapshot3'],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot4'],
		[TestAction.create_volume_snapshot, 'vm1-root', 'vm1-root-snapshot8'],
		[TestAction.create_volume_snapshot, 'volume1', 'volume1-snapshot9'],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot10'],
		[TestAction.create_volume_snapshot, 'vm1-root', 'vm1-root-snapshot14'],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot15'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.use_vm_snapshot, 'vm1-snapshot4'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.resize_volume, 'vm1', 5*1024*1024],
		[TestAction.delete_volume_snapshot, 'volume1-snapshot1'],
		[TestAction.delete_volume_snapshot, 'volume1-snapshot4'],
		TestAction.batch_delete_snapshots, ['volume2-snapshot4','volume3-snapshot15',],
])



'''
The final status:
Running:['vm1']
Stopped:[]
Enadbled:['volume2-snapshot2', 'vm1-root-snapshot3', 'vm1-snapshot4', 'volume3-snapshot4', 'vm1-root-snapshot8', 'volume1-snapshot9', 'vm1-snapshot10', 'volume1-snapshot10', 'volume2-snapshot10', 'volume3-snapshot10', 'vm1-root-snapshot14', 'vm1-snapshot15', 'volume1-snapshot15', 'volume2-snapshot15']
attached:['volume1', 'volume2', 'volume3']
Detached:[]
Deleted:['volume1-snapshot1', 'volume1-snapshot4', 'volume2-snapshot4', 'volume3-snapshot15']
Expunged:[]
Ha:[]
Group:
	vm_snap2:['vm1-snapshot10', 'volume1-snapshot10', 'volume2-snapshot10', 'volume3-snapshot10']---vm1volume1_volume2_volume3
'''