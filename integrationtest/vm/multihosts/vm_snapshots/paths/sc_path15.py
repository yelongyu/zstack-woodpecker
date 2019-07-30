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
		[TestAction.create_volume_snapshot, 'volume3', 'volume3-snapshot10'],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot11'],
		[TestAction.create_volume_snapshot, 'vm1-root', 'vm1-root-snapshot15'],
		[TestAction.create_volume_snapshot, 'vm1-root', 'vm1-root-snapshot16'],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot17'],
		[TestAction.create_volume_snapshot, 'volume2', 'volume2-snapshot21'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.use_volume_snapshot, 'volume3-snapshot1'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.resize_data_volume, 'volume1', 5*1024*1024],
		[TestAction.delete_volume_snapshot, 'volume1-snapshot1'],
		[TestAction.delete_volume_snapshot, 'volume1-snapshot6'],
		[TestAction.delete_vm_snapshot, 'vm1-snapshot1'],
])



'''
The final status:
Running:['vm1']
Stopped:[]
Enadbled:['volume2-snapshot5', 'vm1-snapshot6', 'volume2-snapshot6', 'volume3-snapshot6', 'volume3-snapshot10', 'vm1-snapshot11', 'volume1-snapshot11', 'volume2-snapshot11', 'volume3-snapshot11', 'vm1-root-snapshot15', 'vm1-root-snapshot16', 'vm1-snapshot17', 'volume1-snapshot17', 'volume2-snapshot17', 'volume3-snapshot17', 'volume2-snapshot21']
attached:['volume1', 'volume2', 'volume3']
Detached:[]
Deleted:['volume1-snapshot6', 'vm1-snapshot1', 'volume1-snapshot1', 'volume2-snapshot1', 'volume3-snapshot1']
Expunged:[]
Ha:[]
Group:
	vm_snap2:['vm1-snapshot6', 'volume1-snapshot6', 'volume2-snapshot6', 'volume3-snapshot6']---vm1volume1_volume2_volume3
	vm_snap3:['vm1-snapshot11', 'volume1-snapshot11', 'volume2-snapshot11', 'volume3-snapshot11']---vm1volume1_volume2_volume3
	vm_snap4:['vm1-snapshot17', 'volume1-snapshot17', 'volume2-snapshot17', 'volume3-snapshot17']---vm1volume1_volume2_volume3
'''