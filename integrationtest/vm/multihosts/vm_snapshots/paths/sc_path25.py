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
		[TestAction.create_volume_snapshot, 'volume3', 'volume3-snapshot3'],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot4'],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot5'],
		[TestAction.create_volume_snapshot, 'volume1', 'volume1-snapshot6'],
		[TestAction.create_volume_snapshot, 'volume1', 'volume1-snapshot7'],
		[TestAction.create_volume_snapshot, 'volume3', 'volume3-snapshot8'],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot9'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.use_vm_snapshot, 'vm1-snapshot1'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.reboot_vm, 'vm1'],
		[TestAction.delete_volume_snapshot, 'volume1-snapshot6'],
		[TestAction.delete_volume_snapshot, 'volume3-snapshot3'],
		[TestAction.delete_volume_snapshot, 'volume3-snapshot8'],
])



'''
The final status:
Running:['vm1']
Stopped:[]
Enadbled:['vm1-snapshot1', 'vm1-snapshot2', 'vm1-snapshot4', 'vm1-snapshot5', 'volume1-snapshot7', 'vm1-snapshot9']
attached:[]
Detached:['volume1', 'volume2', 'volume3']
Deleted:['volume1-snapshot6', 'volume3-snapshot3', 'volume3-snapshot8']
Expunged:[]
Ha:[]
Group:
	vm_snap2:['vm1-snapshot2']---vm1
	vm_snap3:['vm1-snapshot4']---vm1
	vm_snap1:['vm1-snapshot1']---vm1
	vm_snap4:['vm1-snapshot5']---vm1
	vm_snap5:['vm1-snapshot9']---vm1
'''