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
		[TestAction.create_volume_snapshot, 'vm1-root', 'vm1-root-snapshot5'],
		[TestAction.create_data_vol_template_from_volume, 'volume3', 'volume3-image1'],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot6'],
		[TestAction.clone_vm, 'vm1', 'vm2', 'full'],
		[TestAction.create_vm_snapshot, 'vm2', 'vm2-snapshot10'],
		[TestAction.create_volume_backup, 'vm1-root', 'vm1-root-backup1'],
		[TestAction.create_data_vol_template_from_volume, 'volume3', 'volume3-image2'],
		[TestAction.stop_vm, 'vm2'],
		[TestAction.ps_migrate_vm, 'vm2'],
		[TestAction.start_vm, 'vm2'],
		[TestAction.delete_vm_snapshot, 'vm2-snapshot10'],
])



'''
The final status:
Running:['vm1', 'vm2']
Stopped:[]
Enadbled:['vm1-snapshot1', 'volume1-snapshot1', 'volume2-snapshot1', 'volume3-snapshot1', 'vm1-root-snapshot5', 'vm1-snapshot6', 'volume1-snapshot6', 'volume2-snapshot6', 'volume3-snapshot6', 'vm1-root-backup1', 'volume3-image1', 'volume3-image2']
attached:['volume1', 'volume2', 'volume3', 'clone@volume1', 'clone@volume2', 'clone@volume3']
Detached:[]
Deleted:['vm2-snapshot10', 'clone@volume1-snapshot10', 'clone@volume2-snapshot10', 'clone@volume3-snapshot10']
Expunged:[]
Ha:[]
Group:
	vm_snap2:['vm1-snapshot6', 'volume1-snapshot6', 'volume2-snapshot6', 'volume3-snapshot6']---vm1@volume1_volume2_volume3
	vm_snap1:['vm1-snapshot1', 'volume1-snapshot1', 'volume2-snapshot1', 'volume3-snapshot1']---vm1@volume1_volume2_volume3
'''