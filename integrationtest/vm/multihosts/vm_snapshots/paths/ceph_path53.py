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
		[TestAction.ps_migrate_vm, 'vm1'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.create_volume_backup, 'volume2', 'volume2-backup1'],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot5'],
		[TestAction.clone_vm, 'vm1', 'vm2', 'full'],
		[TestAction.create_vm_snapshot, 'vm2', 'vm2-snapshot9'],
		[TestAction.reboot_vm, 'vm1'],
		[TestAction.create_volume, 'volume7', 'flag=scsi'],
		[TestAction.attach_volume, 'vm2', 'volume7'],
		[TestAction.batch_delete_volume_snapshot, ['volume2-snapshot1','volume1-snapshot1',]],
		[TestAction.delete_vm_snapshot, 'vm1-snapshot5'],
])



'''
The final status:
Running:['vm1', 'vm2']
Stopped:[]
Enadbled:['vm1-snapshot1', 'volume3-snapshot1', 'vm2-snapshot9', 'volume4-snapshot9', 'volume5-snapshot9', 'volume6-snapshot9', 'volume2-backup1']
attached:['volume1', 'volume2', 'volume3', 'volume4', 'volume5', 'volume6', 'volume7']
Detached:[]
Deleted:['volume2-snapshot1', 'volume1-snapshot1', 'vm1-snapshot5', 'volume1-snapshot5', 'volume2-snapshot5', 'volume3-snapshot5']
Expunged:[]
Ha:[]
Group:
	vm_snap3:['vm2-snapshot9', 'volume4-snapshot9', 'volume5-snapshot9', 'volume6-snapshot9']---vm2volume4_volume5_volume6
'''