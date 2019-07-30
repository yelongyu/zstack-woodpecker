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
		[TestAction.create_volume, 'volume4', 'flag=scsi'],
		[TestAction.attach_volume, 'vm1', 'volume4'],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot6'],
		[TestAction.clone_vm, 'vm1', 'vm2'],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot11'],
		[TestAction.create_vm_backup, 'vm2', 'vm2-backup1'],
		[TestAction.create_data_vol_template_from_volume, 'volume2', 'volume2-image1'],
		[TestAction.batch_delete_volume_snapshot, ['volume3-snapshot11','volume4-snapshot11',]],
		[TestAction.delete_vm_snapshot, 'vm1-snapshot1'],
])



'''
The final status:
Running:['vm1', 'vm2']
Stopped:[]
Enadbled:['vm1-root-snapshot5', 'vm1-snapshot6', 'volume1-snapshot6', 'volume2-snapshot6', 'volume3-snapshot6', 'volume4-snapshot6', 'vm1-snapshot11', 'volume1-snapshot11', 'volume2-snapshot11', 'vm2-backup1', 'volume2-image1']
attached:['volume1', 'volume2', 'volume3', 'volume4']
Detached:[]
Deleted:['volume3-snapshot11', 'volume4-snapshot11', 'vm1-snapshot1', 'volume1-snapshot1', 'volume2-snapshot1', 'volume3-snapshot1']
Expunged:[]
Ha:[]
Group:
	vm_snap2:['vm1-snapshot6', 'volume1-snapshot6', 'volume2-snapshot6', 'volume3-snapshot6', 'volume4-snapshot6']---vm1volume1_volume2_volume3_volume4
	vm_backup1:['vm2-backup1']---vm2_
'''