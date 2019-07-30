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
		[TestAction.create_volume_backup, 'volume3', 'volume3-backup1'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.use_volume_backup, 'volume3-backup1'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot5'],
		[TestAction.create_volume_snapshot, 'vm1-root', 'vm1-root-snapshot9'],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot10'],
		[TestAction.batch_delete_volume_snapshot, ['vm1-snapshot10','volume2-snapshot1',]],
		[TestAction.create_volume_backup, 'volume1', 'volume1-backup2'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.use_volume_snapshot, 'vm1-root-snapshot9'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.delete_vm_snapshot, 'vm1-snapshot5'],
])



'''
The final status:
Running:['vm1']
Stopped:[]
Enadbled:['vm1-snapshot1', 'volume1-snapshot1', 'volume3-snapshot1', 'vm1-root-snapshot9', 'volume1-snapshot10', 'volume2-snapshot10', 'volume3-snapshot10', 'volume3-backup1', 'volume1-backup2']
attached:['volume1', 'volume2', 'volume3']
Detached:[]
Deleted:['vm1-snapshot10', 'volume2-snapshot1', 'vm1-snapshot5', 'volume1-snapshot5', 'volume2-snapshot5', 'volume3-snapshot5']
Expunged:[]
Ha:[]
Group:
'''