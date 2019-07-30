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
		[TestAction.create_volume_snapshot, 'volume3', 'volume3-snapshot2'],
		[TestAction.create_volume_snapshot, 'vm1-root', 'vm1-root-snapshot3'],
		[TestAction.create_volume_snapshot, 'vm1-root', 'vm1-root-snapshot4'],
		[TestAction.create_volume_snapshot, 'volume2', 'volume2-snapshot5'],
		[TestAction.create_volume_snapshot, 'vm1-root', 'vm1-root-snapshot6'],
		[TestAction.create_volume_snapshot, 'vm1-root', 'vm1-root-snapshot7'],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot8'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.use_vm_snapshot, 'vm1-snapshot8'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.create_volume_snapshot, 'volume1', 'volume1-snapshot12'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.use_vm_snapshot, 'vm1-snapshot8'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.reboot_vm, 'vm1'],
		[TestAction.delete_volume_snapshot, 'vm1-root-snapshot4'],
		[TestAction.delete_volume_snapshot, 'vm1-root-snapshot1'],
		[TestAction.batch_delete_volume_snapshot, ['vm1-root-snapshot7','volume3-snapshot8',]],
])



'''
The final status:
Running:['vm1']
Stopped:[]
Enadbled:['volume3-snapshot2', 'vm1-root-snapshot3', 'volume2-snapshot5', 'vm1-root-snapshot6', 'vm1-snapshot8', 'volume1-snapshot8', 'volume2-snapshot8', 'volume1-snapshot12']
attached:['volume1', 'volume2', 'volume3']
Detached:[]
Deleted:['vm1-root-snapshot4', 'vm1-root-snapshot1', 'vm1-root-snapshot7', 'volume3-snapshot8']
Expunged:[]
Ha:[]
Group:
'''