import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", path_list=[
		[TestAction.create_vm, 'vm1', ],
		[TestAction.create_volume, 'volume1', 'flag=scsi'],
		[TestAction.attach_volume, 'vm1', 'volume1'],
		[TestAction.create_volume, 'volume2', 'flag=scsi'],
		[TestAction.attach_volume, 'vm1', 'volume2'],
		[TestAction.create_volume, 'volume3', 'flag=scsi'],
		[TestAction.attach_volume, 'vm1', 'volume3'],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot1'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.reinit_vm, 'vm1'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.resize_data_volume, 'volume2', 5*1024*1024],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot5'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.ps_migrate_vm, 'vm1'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot9'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.use_volume_snapshot, 'vm1-snapshot1'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.create_volume, 'volume4', 'flag=scsi'],
		[TestAction.attach_volume, 'vm1', 'volume4'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.use_volume_snapshot, 'vm1-snapshot9'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.delete_vm_snapshot, 'vm1-snapshot1'],
])



'''
The final status:
Running:['vm1']
Stopped:[]
Enadbled:['vm1-snapshot5', 'volume1-snapshot5', 'volume2-snapshot5', 'volume3-snapshot5', 'vm1-snapshot9', 'volume1-snapshot9', 'volume2-snapshot9', 'volume3-snapshot9']
attached:['volume1', 'volume2', 'volume3', 'volume4']
Detached:[]
Deleted:['vm1-snapshot1', 'volume1-snapshot1', 'volume2-snapshot1', 'volume3-snapshot1']
Expunged:[]
Ha:[]
Group:
	vm_snap2:['vm1-snapshot5', 'volume1-snapshot5', 'volume2-snapshot5', 'volume3-snapshot5']---vm1volume1_volume2_volume3
	vm_snap3:['vm1-snapshot9', 'volume1-snapshot9', 'volume2-snapshot9', 'volume3-snapshot9']---vm1volume1_volume2_volume3
'''