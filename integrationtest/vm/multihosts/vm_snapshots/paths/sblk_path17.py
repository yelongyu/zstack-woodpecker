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
		[TestAction.delete_volume, 'volume2'],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot5'],
		[TestAction.clone_vm, 'vm1', 'vm2', 'full'],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot8'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.use_volume_snapshot, 'vm1-snapshot5'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.recover_volume, 'volume2'],
		[TestAction.create_data_vol_template_from_volume, 'volume2', 'volume2-image1'],
		[TestAction.delete_volume, 'volume2'],
		[TestAction.resize_volume, 'vm1', 5*1024*1024],
		[TestAction.delete_vm_snapshot, 'vm1-snapshot1'],
])



'''
The final status:
Running:['vm2', 'vm1']
Stopped:[]
Enadbled:['vm1-snapshot5', 'volume1-snapshot5', 'volume3-snapshot5', 'vm1-snapshot8', 'volume1-snapshot8', 'volume3-snapshot8', 'volume2-image1']
attached:['volume1', 'volume3', 'clone@volume1', 'clone@volume3']
Detached:[]
Deleted:['volume2', 'vm1-snapshot1', 'volume1-snapshot1', 'volume2-snapshot1', 'volume3-snapshot1']
Expunged:[]
Ha:[]
Group:
	vm_snap2:['vm1-snapshot5', 'volume1-snapshot5', 'volume3-snapshot5']---vm1volume1_volume3
	vm_snap3:['vm1-snapshot8', 'volume1-snapshot8', 'volume3-snapshot8']---vm1volume1_volume3
'''