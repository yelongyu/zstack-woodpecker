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
		[TestAction.create_vm_backup, 'vm1', 'vm1-backup1'],
		[TestAction.create_volume, 'volume4', 'flag=scsi'],
		[TestAction.attach_volume, 'vm1', 'volume4'],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot5'],
		[TestAction.create_vm_backup, 'vm1', 'vm1-backup5'],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot10'],
		[TestAction.batch_delete_volume_snapshot, ['volume1-snapshot1','vm1-snapshot5',]],
		[TestAction.migrate_volume, 'volume4'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.change_vm_image, 'vm1'],
		[TestAction.delete_vm_snapshot, 'vm1-snapshot10'],
])



'''
The final status:
Running:[]
Stopped:['vm1']
Enadbled:['vm1-snapshot1', 'volume2-snapshot1', 'volume3-snapshot1', 'volume1-snapshot5', 'volume2-snapshot5', 'volume3-snapshot5', 'volume4-snapshot5', 'vm1-backup1', 'volume1-backup1', 'volume2-backup1', 'volume3-backup1', 'vm1-backup5', 'volume1-backup5', 'volume2-backup5', 'volume3-backup5', 'volume4-backup5']
attached:['volume1', 'volume2', 'volume3', 'volume4']
Detached:[]
Deleted:['volume1-snapshot1', 'vm1-snapshot5', 'vm1-snapshot10', 'volume1-snapshot10', 'volume2-snapshot10', 'volume3-snapshot10', 'volume4-snapshot10']
Expunged:[]
Ha:[]
Group:
	vm_backup2:['vm1-backup5', 'volume1-backup5', 'volume2-backup5', 'volume3-backup5', 'volume4-backup5']---vm1_volume1_volume2_volume3_volume4
	vm_backup1:['vm1-backup1', 'volume1-backup1', 'volume2-backup1', 'volume3-backup1']---vm1_volume1_volume2_volume3
'''