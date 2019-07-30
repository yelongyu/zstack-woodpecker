import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", path_list=[
		[TestAction.create_vm, 'vm1', 'flag=sblk'],
		[TestAction.create_volume, 'volume1', 'flag=ceph,scsi'],
		[TestAction.create_volume, 'volume2', 'flag=sblk,scsi'],
		[TestAction.create_volume, 'volume3', 'flag=ceph,scsi'],
		[TestAction.create_volume_snapshot, 'volume2', 'volume2-snapshot1'],
		[TestAction.create_volume_snapshot, 'vm1-root', 'vm1-root-snapshot2'],
		[TestAction.create_volume_snapshot, 'vm1-root', 'vm1-root-snapshot3'],
		[TestAction.create_volume_snapshot, 'vm1-root', 'vm1-root-snapshot4'],
		[TestAction.create_volume_snapshot, 'volume3', 'volume3-snapshot5'],
		[TestAction.create_volume_snapshot, 'volume1', 'volume1-snapshot6'],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot7'],
		[TestAction.create_volume_snapshot, 'volume3', 'volume3-snapshot8'],
		[TestAction.create_volume_snapshot, 'vm1-root', 'vm1-root-snapshot9'],
		[TestAction.use_volume_snapshot, 'volume3-snapshot5'],
		[TestAction.resize_data_volume, 'volume3', 5*1024*1024],
		[TestAction.delete_volume_snapshot, 'vm1-root-snapshot2'],
		[TestAction.batch_delete_volume_snapshot, ['vm1-snapshot7','vm1-root-snapshot4',]],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot10'],
		[TestAction.delete_vm_snapshot, 'vm1-snapshot10'],
])



'''
The final status:
Running:['vm1']
Stopped:[]
Enadbled:['volume2-snapshot1', 'vm1-root-snapshot3', 'volume3-snapshot5', 'volume1-snapshot6', 'volume3-snapshot8', 'vm1-root-snapshot9']
attached:[]
Detached:['volume1', 'volume2', 'volume3']
Deleted:['vm1-root-snapshot2', 'vm1-snapshot7', 'vm1-root-snapshot4', 'vm1-snapshot10']
Expunged:[]
Ha:[]
Group:
'''