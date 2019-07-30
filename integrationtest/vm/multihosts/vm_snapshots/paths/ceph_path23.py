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
		[TestAction.clone_vm, 'vm1', 'vm2'],
		[TestAction.delete_volume, 'volume3'],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot5'],
		[TestAction.batch_delete_volume_snapshot, ['volume2-snapshot1','vm1-snapshot1',]],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot8'],
		[TestAction.migrate_vm, 'vm1'],
		[TestAction.migrate_volume, 'volume1'],
		[TestAction.delete_vm_snapshot, 'vm1-snapshot5'],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot11'],
		[TestAction.delete_vm_snapshot, 'vm1-snapshot11'],
])



'''
The final status:
Running:['vm1', 'vm2']
Stopped:[]
Enadbled:['volume1-snapshot1', 'volume3-snapshot1', 'vm1-snapshot5', 'volume1-snapshot5', 'volume2-snapshot5']
attached:['volume1', 'volume2']
Detached:[]
Deleted:['volume3', 'volume2-snapshot1', 'vm1-snapshot1', 'vm1-snapshot8', 'volume1-snapshot8', 'volume2-snapshot8', 'vm1-snapshot11', 'volume1-snapshot11', 'volume2-snapshot11']
Expunged:[]
Ha:[]
Group:
'''