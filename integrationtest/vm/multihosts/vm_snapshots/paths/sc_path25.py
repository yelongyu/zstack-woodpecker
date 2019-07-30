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
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot5'],
		[TestAction.create_volume_snapshot, 'volume2', 'volume2-snapshot9'],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot10'],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot14'],
		[TestAction.create_volume_snapshot, 'volume3', 'volume3-snapshot18'],
		[TestAction.create_volume_snapshot, 'volume1', 'volume1-snapshot19'],
		[TestAction.create_volume_snapshot, 'volume2', 'volume2-snapshot20'],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot21'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.use_vm_snapshot, 'vm1-snapshot1'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.reboot_vm, 'vm1'],
		[TestAction.delete_volume_snapshot, 'volume1-snapshot1'],
		[TestAction.delete_volume_snapshot, 'volume2-snapshot1'],
		[TestAction.delete_volume_snapshot, 'volume1-snapshot5'],
])



'''
The final status:
Running:['vm1']
Stopped:[]
Enadbled:['vm1-snapshot1', 'volume3-snapshot1', 'vm1-snapshot5', 'volume2-snapshot5', 'volume3-snapshot5', 'volume2-snapshot9', 'vm1-snapshot10', 'volume1-snapshot10', 'volume2-snapshot10', 'volume3-snapshot10', 'vm1-snapshot14', 'volume1-snapshot14', 'volume2-snapshot14', 'volume3-snapshot14', 'volume3-snapshot18', 'volume1-snapshot19', 'volume2-snapshot20', 'vm1-snapshot21', 'volume1-snapshot21', 'volume2-snapshot21', 'volume3-snapshot21']
attached:['volume1', 'volume2', 'volume3']
Detached:[]
Deleted:['volume1-snapshot1', 'volume2-snapshot1', 'volume1-snapshot5']
Expunged:[]
Ha:[]
Group:
	vm_snap2:['vm1-snapshot5', 'volume1-snapshot5', 'volume2-snapshot5', 'volume3-snapshot5']---vm1volume1_volume2_volume3
	vm_snap3:['vm1-snapshot10', 'volume1-snapshot10', 'volume2-snapshot10', 'volume3-snapshot10']---vm1volume1_volume2_volume3
	vm_snap1:['vm1-snapshot1', 'volume1-snapshot1', 'volume2-snapshot1', 'volume3-snapshot1']---vm1volume1_volume2_volume3
	vm_snap4:['vm1-snapshot14', 'volume1-snapshot14', 'volume2-snapshot14', 'volume3-snapshot14']---vm1volume1_volume2_volume3
	vm_snap5:['vm1-snapshot21', 'volume1-snapshot21', 'volume2-snapshot21', 'volume3-snapshot21']---vm1volume1_volume2_volume3
'''