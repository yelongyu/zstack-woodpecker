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
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot1'],
		[TestAction.create_volume_snapshot, 'volume2', 'volume2-snapshot5'],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot6'],
		[TestAction.create_volume_snapshot, 'volume2', 'volume2-snapshot10'],
		[TestAction.create_volume_snapshot, 'vm1-root', 'vm1-root-snapshot11'],
		[TestAction.create_volume_snapshot, 'vm1-root', 'vm1-root-snapshot12'],
		[TestAction.create_volume_snapshot, 'volume1', 'volume1-snapshot13'],
		[TestAction.create_volume_snapshot, 'volume1', 'volume1-snapshot14'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.use_vm_snapshot, 'vm1-snapshot1'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.use_vm_snapshot, 'vm1-snapshot1'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.reinit_vm, 'vm1'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.batch_delete_volume_snapshot, ['vm1-root-snapshot12','volume1-snapshot13',]],
		[TestAction.delete_vm_snapshot, 'vm1-snapshot1'],
		[TestAction.delete_vm_snapshot, 'vm1-snapshot6'],
])



'''
The final status:
Running:['vm1']
Stopped:[]
Enadbled:['volume2-snapshot5', 'volume2-snapshot10', 'vm1-root-snapshot11', 'volume1-snapshot14']
attached:['volume1', 'volume2', 'volume3']
Detached:[]
Deleted:['vm1-root-snapshot12', 'volume1-snapshot13', 'vm1-snapshot1', 'volume1-snapshot1', 'volume2-snapshot1', 'volume3-snapshot1', 'vm1-snapshot6', 'volume1-snapshot6', 'volume2-snapshot6', 'volume3-snapshot6']
Expunged:[]
Ha:[]
Group:
'''