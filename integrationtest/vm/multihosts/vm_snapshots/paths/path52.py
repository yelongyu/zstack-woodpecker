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
		[TestAction.create_volume_snapshot, 'volume3', 'volume3-snapshot1'],
		[TestAction.create_volume_snapshot, 'vm1-root', 'vm1-root-snapshot2'],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot3'],
		[TestAction.create_volume_snapshot, 'vm1-root', 'vm1-root-snapshot7'],
		[TestAction.create_volume_snapshot, 'vm1-root', 'vm1-root-snapshot8'],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot9'],
		[TestAction.create_volume_snapshot, 'volume2', 'volume2-snapshot13'],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot14'],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot18'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.use_vm_snapshot, 'vm1-snapshot3'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.reinit_vm, 'vm1'],
		[TestAction.delete_volume_snapshot, 'vm1-root-snapshot2'],
		[TestAction.delete_volume_snapshot, 'vm1-root-snapshot8'],
		[TestAction.delete_volume_snapshot, 'volume2-snapshot3'],
])



'''
The final status:
Running:[]
Stopped:['vm1']
Enadbled:['volume3-snapshot1', 'vm1-snapshot3', 'volume1-snapshot3', 'volume3-snapshot3', 'vm1-root-snapshot7', 'vm1-snapshot9', 'volume1-snapshot9', 'volume2-snapshot9', 'volume3-snapshot9', 'volume2-snapshot13', 'vm1-snapshot14', 'volume1-snapshot14', 'volume2-snapshot14', 'volume3-snapshot14', 'vm1-snapshot18', 'volume1-snapshot18', 'volume2-snapshot18', 'volume3-snapshot18']
attached:['volume1', 'volume2', 'volume3']
Detached:[]
Deleted:['vm1-root-snapshot2', 'vm1-root-snapshot8', 'volume2-snapshot3']
Expunged:[]
Ha:[]
Group:
	vm_snap2:['vm1-snapshot9', 'volume1-snapshot9', 'volume2-snapshot9', 'volume3-snapshot9']---vm1volume1_volume2_volume3
	vm_snap3:['vm1-snapshot14', 'volume1-snapshot14', 'volume2-snapshot14', 'volume3-snapshot14']---vm1volume1_volume2_volume3
	vm_snap1:['vm1-snapshot3', 'volume1-snapshot3', 'volume2-snapshot3', 'volume3-snapshot3']---vm1volume1_volume2_volume3
	vm_snap4:['vm1-snapshot18', 'volume1-snapshot18', 'volume2-snapshot18', 'volume3-snapshot18']---vm1volume1_volume2_volume3
'''