import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", checking_point=8, path_list=[
		[TestAction.create_vm, 'vm1', ],
		[TestAction.create_volume, 'volume1', 'flag=scsi'],
		[TestAction.attach_volume, 'vm1', 'volume1'],
		[TestAction.create_volume, 'volume2', 'flag=scsi'],
		[TestAction.attach_volume, 'vm1', 'volume2'],
		[TestAction.create_volume, 'volume3', 'flag=scsi'],
		[TestAction.attach_volume, 'vm1', 'volume3'],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot1'],
		[TestAction.clone_vm, 'vm1', 'vm2'],
		[TestAction.delete_volume, 'volume1'],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot5'],
		[TestAction.batch_delete_volume_snapshot, ['volume2-snapshot1','volume3-snapshot5',]],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot8'],
		[TestAction.migrate_vm, 'vm2'],
		[TestAction.migrate_volume, 'volume3'],
		[TestAction.delete_vm_snapshot, 'vm1-snapshot8'],
		[TestAction.create_vm_snapshot, 'vm2', 'vm2-snapshot11'],
		[TestAction.delete_vm_snapshot, 'vm2-snapshot11'],
])



'''
The final status:
Running:['vm1', 'vm2']
Stopped:[]
Enadbled:['vm1-snapshot1', 'volume1-snapshot1', 'volume3-snapshot1', 'vm1-snapshot5', 'volume2-snapshot5']
attached:['volume2', 'volume3']
Detached:[]
Deleted:['volume1', 'volume2-snapshot1', 'volume3-snapshot5', 'vm1-snapshot8', 'volume2-snapshot8', 'volume3-snapshot8', 'vm2-snapshot11']
Expunged:[]
Ha:[]
Group:
'''
