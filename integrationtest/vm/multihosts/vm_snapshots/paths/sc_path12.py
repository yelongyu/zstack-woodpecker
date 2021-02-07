import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", checking_point=8, path_list=[
		[TestAction.create_vm, 'vm1', 'flag=sblk'],
		[TestAction.create_volume, 'volume1', 'flag=ceph,scsi'],
		[TestAction.attach_volume, 'vm1', 'volume1'],
		[TestAction.create_volume, 'volume2', 'flag=sblk,scsi'],
		[TestAction.attach_volume, 'vm1', 'volume2'],
		[TestAction.create_volume, 'volume3', 'flag=ceph,scsi'],
		[TestAction.attach_volume, 'vm1', 'volume3'],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot1'],
		[TestAction.create_volume_snapshot, 'vm1-root', 'vm1-root-snapshot5'],
		[TestAction.create_volume_snapshot, 'volume2', 'volume2-snapshot6'],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot7'],
		[TestAction.create_volume_snapshot, 'vm1-root', 'vm1-root-snapshot11'],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot12'],
		[TestAction.create_volume_snapshot, 'volume3', 'volume3-snapshot16'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.use_volume_snapshot, 'volume3-snapshot1'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.use_volume_snapshot, 'vm1-snapshot1'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.use_vm_snapshot, 'vm1-snapshot1'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.reinit_vm, 'vm1'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.delete_volume_snapshot, 'vm1-snapshot1'],
		[TestAction.delete_volume_snapshot, 'volume2-snapshot1'],
		[TestAction.delete_volume_snapshot, 'vm1-root-snapshot5'],
])



'''
The final status:
Running:['vm1']
Stopped:[]
Enadbled:['volume1-snapshot1', 'volume3-snapshot1', 'volume2-snapshot6', 'vm1-snapshot7', 'volume1-snapshot7', 'volume2-snapshot7', 'volume3-snapshot7', 'vm1-root-snapshot11', 'vm1-snapshot12', 'volume1-snapshot12', 'volume2-snapshot12', 'volume3-snapshot12', 'volume3-snapshot16']
attached:['volume1', 'volume2', 'volume3']
Detached:[]
Deleted:['vm1-snapshot1', 'volume2-snapshot1', 'vm1-root-snapshot5']
Expunged:[]
Ha:[]
Group:
	vm_snap2:['vm1-snapshot7', 'volume1-snapshot7', 'volume2-snapshot7', 'volume3-snapshot7']---vm1volume1_volume2_volume3
	vm_snap3:['vm1-snapshot12', 'volume1-snapshot12', 'volume2-snapshot12', 'volume3-snapshot12']---vm1volume1_volume2_volume3
'''
