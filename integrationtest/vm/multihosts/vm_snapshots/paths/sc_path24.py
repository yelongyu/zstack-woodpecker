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
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot5'],
		[TestAction.create_volume_snapshot, 'vm1-root', 'vm1-root-snapshot9'],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot10'],
		[TestAction.create_volume_snapshot, 'volume2', 'volume2-snapshot14'],
		[TestAction.create_volume_snapshot, 'volume3', 'volume3-snapshot15'],
		[TestAction.create_volume_snapshot, 'volume2', 'volume2-snapshot16'],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot17'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.use_volume_snapshot, 'volume3-snapshot1'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.use_vm_snapshot, 'vm1-snapshot1'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.reinit_vm, 'vm1'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.delete_vm_snapshot, 'vm1-snapshot1'],
		[TestAction.delete_volume_snapshot, 'vm1-snapshot5'],
		[TestAction.batch_delete_volume_snapshot, ['volume1-snapshot10','volume3-snapshot17',]],
])



'''
The final status:
Running:['vm1']
Stopped:[]
Enadbled:['volume1-snapshot5', 'volume2-snapshot5', 'volume3-snapshot5', 'vm1-root-snapshot9', 'vm1-snapshot10', 'volume2-snapshot10', 'volume3-snapshot10', 'volume2-snapshot14', 'volume3-snapshot15', 'volume2-snapshot16', 'vm1-snapshot17', 'volume1-snapshot17', 'volume2-snapshot17']
attached:['volume1', 'volume2', 'volume3']
Detached:[]
Deleted:['vm1-snapshot1', 'volume1-snapshot1', 'volume2-snapshot1', 'volume3-snapshot1', 'vm1-snapshot5', 'volume1-snapshot10', 'volume3-snapshot17']
Expunged:[]
Ha:[]
Group:
'''
