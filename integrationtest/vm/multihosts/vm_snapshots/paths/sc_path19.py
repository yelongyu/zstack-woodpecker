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
		[TestAction.create_volume_snapshot, 'vm1-root', 'vm1-root-snapshot1'],
		[TestAction.create_volume_snapshot, 'vm1-root', 'vm1-root-snapshot2'],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot3'],
		[TestAction.create_volume_snapshot, 'volume3', 'volume3-snapshot7'],
		[TestAction.create_volume_snapshot, 'volume3', 'volume3-snapshot8'],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot9'],
		[TestAction.create_volume_snapshot, 'vm1-root', 'vm1-root-snapshot13'],
		[TestAction.create_volume_snapshot, 'vm1-root', 'vm1-root-snapshot14'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.use_volume_snapshot, 'vm1-root-snapshot1'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.use_volume_snapshot, 'vm1-root-snapshot2'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.resize_volume, 'vm1', 5*1024*1024],
		[TestAction.delete_vm_snapshot, 'vm1-snapshot3'],
		[TestAction.delete_volume_snapshot, 'vm1-snapshot9'],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot15'],
		[TestAction.delete_vm_snapshot, 'vm1-snapshot15'],
])



'''
The final status:
Running:['vm1']
Stopped:[]
Enadbled:['vm1-root-snapshot1', 'vm1-root-snapshot2', 'volume3-snapshot7', 'volume3-snapshot8', 'volume1-snapshot9', 'volume2-snapshot9', 'volume3-snapshot9', 'vm1-root-snapshot13', 'vm1-root-snapshot14']
attached:['volume1', 'volume2', 'volume3']
Detached:[]
Deleted:['vm1-snapshot3', 'volume1-snapshot3', 'volume2-snapshot3', 'volume3-snapshot3', 'vm1-snapshot9', 'vm1-snapshot15', 'volume1-snapshot15', 'volume2-snapshot15', 'volume3-snapshot15']
Expunged:[]
Ha:[]
Group:
'''
