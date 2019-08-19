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
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot2'],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot6'],
		[TestAction.create_volume_snapshot, 'volume2', 'volume2-snapshot10'],
		[TestAction.create_volume_snapshot, 'volume2', 'volume2-snapshot11'],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot12'],
		[TestAction.create_volume_snapshot, 'volume2', 'volume2-snapshot16'],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot17'],
		[TestAction.create_volume_snapshot, 'vm1-root', 'vm1-root-snapshot21'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.use_volume_snapshot, 'vm1-snapshot2'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.reboot_vm, 'vm1'],
		[TestAction.delete_volume_snapshot, 'volume2-snapshot2'],
		[TestAction.delete_vm_snapshot, 'vm1-snapshot2'],
		[TestAction.delete_volume_snapshot, 'vm1-snapshot12'],
])



'''
The final status:
Running:['vm1']
Stopped:[]
Enadbled:['vm1-root-snapshot1', 'vm1-snapshot6', 'volume1-snapshot6', 'volume2-snapshot6', 'volume3-snapshot6', 'volume2-snapshot10', 'volume2-snapshot11', 'volume1-snapshot12', 'volume2-snapshot12', 'volume3-snapshot12', 'volume2-snapshot16', 'vm1-snapshot17', 'volume1-snapshot17', 'volume2-snapshot17', 'volume3-snapshot17', 'vm1-root-snapshot21']
attached:['volume1', 'volume2', 'volume3']
Detached:[]
Deleted:['vm1-snapshot2', 'volume1-snapshot2', 'volume2-snapshot2', 'volume3-snapshot2', 'vm1-snapshot12']
Expunged:[]
Ha:[]
Group:
	vm_snap2:['vm1-snapshot6', 'volume1-snapshot6', 'volume2-snapshot6', 'volume3-snapshot6']---vm1volume1_volume2_volume3
	vm_snap4:['vm1-snapshot17', 'volume1-snapshot17', 'volume2-snapshot17', 'volume3-snapshot17']---vm1volume1_volume2_volume3
'''
