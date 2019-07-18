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
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot5'],
		[TestAction.create_volume_snapshot, 'vm1-root', 'vm1-root-snapshot9'],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot10'],
		[TestAction.create_volume_snapshot, 'volume1', 'volume1-snapshot14'],
		[TestAction.create_volume_snapshot, 'volume3', 'volume3-snapshot15'],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot16'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.use_volume_snapshot, 'volume2-snapshot1'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.create_volume_snapshot, 'vm1-root', 'vm1-root-snapshot20'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.use_volume_snapshot, 'volume3-snapshot1'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.reinit_vm, 'vm1'],
		[TestAction.delete_volume_snapshot, 'volume2-snapshot1'],
		TestAction.batch_delete_snapshots, ['vm1-snapshot1','vm1-snapshot10',],
		[TestAction.delete_volume_snapshot, 'vm1-root-snapshot20'],
])



'''
The final status:
Running:[]
Stopped:['vm1']
Enadbled:['volume1-snapshot1', 'volume3-snapshot1', 'vm1-snapshot5', 'volume1-snapshot5', 'volume2-snapshot5', 'volume3-snapshot5', 'vm1-root-snapshot9', 'volume1-snapshot10', 'volume2-snapshot10', 'volume3-snapshot10', 'volume1-snapshot14', 'volume3-snapshot15', 'vm1-snapshot16', 'volume1-snapshot16', 'volume2-snapshot16', 'volume3-snapshot16']
attached:['volume1', 'volume2', 'volume3']
Detached:[]
Deleted:['volume2-snapshot1', 'vm1-snapshot1', 'vm1-snapshot10', 'vm1-root-snapshot20']
Expunged:[]
Ha:[]
Group:
	vm_snap2:['vm1-snapshot5', 'volume1-snapshot5', 'volume2-snapshot5', 'volume3-snapshot5']---vm1volume1_volume2_volume3
	vm_snap4:['vm1-snapshot16', 'volume1-snapshot16', 'volume2-snapshot16', 'volume3-snapshot16']---vm1volume1_volume2_volume3
'''