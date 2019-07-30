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
		[TestAction.create_volume_snapshot, 'volume1', 'volume1-snapshot6'],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot7'],
		[TestAction.migrate_vm, 'vm1'],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot11'],
		[TestAction.batch_delete_volume_snapshot, ['volume2-snapshot11','volume1-snapshot1',]],
		[TestAction.delete_volume_snapshot, 'vm1-snapshot7'],
		[TestAction.create_volume_backup, 'vm1-root', 'vm1-root-backup1'],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot15'],
		[TestAction.delete_vm_snapshot, 'vm1-snapshot15'],
])



'''
The final status:
Running:['vm1']
Stopped:[]
Enadbled:['vm1-snapshot1', 'volume2-snapshot1', 'volume3-snapshot1', 'vm1-root-snapshot5', 'volume1-snapshot6', 'volume1-snapshot7', 'volume2-snapshot7', 'volume3-snapshot7', 'vm1-snapshot11', 'volume1-snapshot11', 'volume3-snapshot11', 'vm1-root-backup1']
attached:['volume1', 'volume2', 'volume3']
Detached:[]
Deleted:['volume2-snapshot11', 'volume1-snapshot1', 'vm1-snapshot7', 'vm1-snapshot15', 'volume1-snapshot15', 'volume2-snapshot15', 'volume3-snapshot15']
Expunged:[]
Ha:[]
Group:
'''