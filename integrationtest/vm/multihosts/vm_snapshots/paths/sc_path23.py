import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", path_list=[
		[TestAction.create_vm, 'vm1', 'flag=sblk'],
		[TestAction.create_volume, 'volume1', 'flag=ceph,scsi'],
		[TestAction.attach_volume, 'vm1', 'volume1'],
		[TestAction.create_volume, 'volume2', 'flag=sblk,scsi'],
		[TestAction.attach_volume, 'vm1', 'volume2'],
		[TestAction.create_volume, 'volume3', 'flag=ceph,scsi'],
		[TestAction.attach_volume, 'vm1', 'volume3'],
		[TestAction.create_volume_snapshot, 'vm1-root', 'vm1-root-snapshot1'],
		[TestAction.create_volume_snapshot, 'volume2', 'volume2-snapshot2'],
		[TestAction.create_volume_snapshot, 'vm1-root', 'vm1-root-snapshot3'],
		[TestAction.create_volume_snapshot, 'volume2', 'volume2-snapshot4'],
		[TestAction.create_volume_snapshot, 'vm1-root', 'vm1-root-snapshot5'],
		[TestAction.create_volume_snapshot, 'volume3', 'volume3-snapshot6'],
		[TestAction.create_volume_snapshot, 'volume2', 'volume2-snapshot7'],
		[TestAction.create_volume_snapshot, 'vm1-root', 'vm1-root-snapshot8'],
		[TestAction.create_volume_snapshot, 'vm1-root', 'vm1-root-snapshot9'],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot10'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.use_vm_snapshot, 'vm1-snapshot10'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.create_vm_backup, 'vm1', 'vm1-backup1'],
		[TestAction.delete_volume_snapshot, 'vm1-root-snapshot3'],
		[TestAction.delete_volume_snapshot, 'vm1-root-snapshot5'],
		[TestAction.delete_volume_snapshot, 'volume3-snapshot6'],
])



'''
The final status:
Running:['vm1']
Stopped:[]
Enadbled:['vm1-root-snapshot1', 'volume2-snapshot2', 'volume2-snapshot4', 'volume2-snapshot7', 'vm1-root-snapshot8', 'vm1-root-snapshot9', 'vm1-snapshot10', 'volume1-snapshot10', 'volume2-snapshot10', 'volume3-snapshot10', 'vm1-backup1', 'volume1-backup1', 'volume2-backup1', 'volume3-backup1']
attached:['volume1', 'volume2', 'volume3']
Detached:[]
Deleted:['vm1-root-snapshot3', 'vm1-root-snapshot5', 'volume3-snapshot6']
Expunged:[]
Ha:[]
Group:
	vm_snap1:['vm1-snapshot10', 'volume1-snapshot10', 'volume2-snapshot10', 'volume3-snapshot10']---vm1volume1_volume2_volume3
	vm_backup1:['vm1-backup1', 'volume1-backup1', 'volume2-backup1', 'volume3-backup1']---vm1_volume1_volume2_volume3
'''