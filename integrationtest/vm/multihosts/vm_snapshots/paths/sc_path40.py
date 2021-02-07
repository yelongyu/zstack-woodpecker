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
		[TestAction.create_volume_snapshot, 'volume3', 'volume3-snapshot6'],
		[TestAction.create_volume_snapshot, 'vm1-root', 'vm1-root-snapshot7'],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot8'],
		[TestAction.create_volume_snapshot, 'vm1-root', 'vm1-root-snapshot12'],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot13'],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot17'],
		[TestAction.create_volume_snapshot, 'volume3', 'volume3-snapshot21'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.use_volume_snapshot, 'volume1-snapshot1'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.resize_volume, 'vm1', 5*1024*1024],
		[TestAction.delete_volume_snapshot, 'volume3-snapshot1'],
		[TestAction.delete_volume_snapshot, 'volume1-snapshot1'],
		[TestAction.delete_volume_snapshot, 'vm1-snapshot8'],
])



'''
The final status:
Running:['vm1']
Stopped:[]
Enadbled:['vm1-snapshot1', 'volume2-snapshot1', 'vm1-root-snapshot5', 'volume3-snapshot6', 'vm1-root-snapshot7', 'volume1-snapshot8', 'volume2-snapshot8', 'volume3-snapshot8', 'vm1-root-snapshot12', 'vm1-snapshot13', 'volume1-snapshot13', 'volume2-snapshot13', 'volume3-snapshot13', 'vm1-snapshot17', 'volume1-snapshot17', 'volume2-snapshot17', 'volume3-snapshot17', 'volume3-snapshot21']
attached:['volume1', 'volume2', 'volume3']
Detached:[]
Deleted:['volume3-snapshot1', 'volume1-snapshot1', 'vm1-snapshot8']
Expunged:[]
Ha:[]
Group:
	vm_snap3:['vm1-snapshot13', 'volume1-snapshot13', 'volume2-snapshot13', 'volume3-snapshot13']---vm1volume1_volume2_volume3
	vm_snap1:['vm1-snapshot1', 'volume1-snapshot1', 'volume2-snapshot1', 'volume3-snapshot1']---vm1volume1_volume2_volume3
	vm_snap4:['vm1-snapshot17', 'volume1-snapshot17', 'volume2-snapshot17', 'volume3-snapshot17']---vm1volume1_volume2_volume3
'''
