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
		[TestAction.create_volume_backup, 'vm1-root', 'vm1-root-backup1'],
		[TestAction.create_volume_backup, 'volume3', 'volume3-backup2'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.use_volume_backup, 'volume3-backup2'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot5'],
		[TestAction.batch_delete_volume_snapshot, ['volume3-snapshot1','volume1-snapshot5',]],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot9'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.ps_migrate_vm, 'vm1'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.delete_volume_snapshot, 'volume3-snapshot5'],
		[TestAction.create_volume_backup, 'vm1-root', 'vm1-root-backup3'],
		[TestAction.delete_vm_snapshot, 'vm1-snapshot9'],
])



'''
The final status:
Running:['vm1']
Stopped:[]
Enadbled:['vm1-snapshot1', 'volume1-snapshot1', 'volume2-snapshot1', 'vm1-snapshot5', 'volume2-snapshot5', 'vm1-root-backup1', 'volume3-backup2', 'vm1-root-backup3']
attached:['volume1', 'volume2', 'volume3']
Detached:[]
Deleted:['volume3-snapshot1', 'volume1-snapshot5', 'volume3-snapshot5', 'vm1-snapshot9', 'volume1-snapshot9', 'volume2-snapshot9', 'volume3-snapshot9']
Expunged:[]
Ha:[]
Group:
'''