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
		[TestAction.clone_vm, 'vm1', 'vm2', 'full'],
		[TestAction.create_volume_backup, 'clone@volume2', 'clone@volume2-backup1'],
		[TestAction.create_vm_snapshot, 'vm2', 'vm2-snapshot5'],
		[TestAction.clone_vm, 'vm1', 'vm3'],
		[TestAction.create_vm_snapshot, 'vm3', 'vm3-snapshot9'],
		[TestAction.create_volume_snapshot, 'vm2-root', 'vm2-root-snapshot10'],
		[TestAction.resize_data_volume, 'volume1', 5*1024*1024],
		[TestAction.stop_vm, 'vm2'],
		[TestAction.change_vm_image, 'vm2'],
		[TestAction.delete_vm_snapshot, 'vm2-snapshot5'],
])



'''
The final status:
Running:['vm1', 'vm3']
Stopped:['vm2']
Enadbled:['vm1-snapshot1', 'volume1-snapshot1', 'volume2-snapshot1', 'volume3-snapshot1', 'vm3-snapshot9', 'vm2-root-snapshot10', 'clone@volume2-backup1']
attached:['volume1', 'volume2', 'volume3', 'clone@volume1', 'clone@volume2', 'clone@volume3']
Detached:[]
Deleted:['vm2-snapshot5', 'clone@volume1-snapshot5', 'clone@volume2-snapshot5', 'clone@volume3-snapshot5']
Expunged:[]
Ha:[]
Group:
	vm_snap3:['vm3-snapshot9']---vm3@
	vm_snap1:['vm1-snapshot1', 'volume1-snapshot1', 'volume2-snapshot1', 'volume3-snapshot1']---vm1@volume1_volume2_volume3
'''