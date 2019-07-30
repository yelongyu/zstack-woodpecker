import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", path_list=[
		[TestAction.create_vm, 'vm1', 'flag=sblk'],
		[TestAction.create_volume, 'volume1', 'flag=ceph,scsi'],
		[TestAction.create_volume, 'volume2', 'flag=sblk,scsi'],
		[TestAction.create_volume, 'volume3', 'flag=ceph,scsi'],
		[TestAction.create_volume_snapshot, 'volume3', 'volume3-snapshot1'],
		[TestAction.create_volume_snapshot, 'vm1-root', 'vm1-root-snapshot2'],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot3'],
		[TestAction.create_volume_snapshot, 'volume2', 'volume2-snapshot4'],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot5'],
		[TestAction.create_volume_snapshot, 'vm1-root', 'vm1-root-snapshot6'],
		[TestAction.create_volume_snapshot, 'volume3', 'volume3-snapshot7'],
		[TestAction.use_volume_snapshot, 'volume2-snapshot4'],
		[TestAction.create_volume_snapshot, 'volume2', 'volume2-snapshot8'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.use_volume_snapshot, 'vm1-snapshot3'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.resize_volume, 'vm1', 5*1024*1024],
		[TestAction.delete_volume_snapshot, 'vm1-root-snapshot2'],
		[TestAction.delete_vm_snapshot, 'vm1-snapshot3'],
		[TestAction.delete_vm_snapshot, 'vm1-snapshot5'],
])



'''
The final status:
Running:['vm1']
Stopped:[]
Enadbled:['volume3-snapshot1', 'volume2-snapshot4', 'vm1-root-snapshot6', 'volume3-snapshot7', 'volume2-snapshot8']
attached:[]
Detached:['volume1', 'volume2', 'volume3']
Deleted:['vm1-root-snapshot2', 'vm1-snapshot3', 'vm1-snapshot5']
Expunged:[]
Ha:[]
Group:
'''