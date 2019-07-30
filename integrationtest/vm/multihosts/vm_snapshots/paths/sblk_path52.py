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
		[TestAction.use_volume_snapshot, 'vm1-snapshot1'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.create_volume, 'volume4', 'flag=scsi'],
		[TestAction.attach_volume, 'vm1', 'volume4'],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot5'],
		[TestAction.batch_delete_volume_snapshot, ['volume2-snapshot5','volume3-snapshot1',]],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot10'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.use_volume_snapshot, 'vm1-snapshot5'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.detach_volume, 'volume1'],
		[TestAction.migrate_vm, 'vm1'],
		[TestAction.delete_vm_snapshot, 'vm1-snapshot10'],
])



'''
The final status:
Running:['vm1']
Stopped:[]
Enadbled:['vm1-snapshot1', 'volume1-snapshot1', 'volume2-snapshot1', 'vm1-snapshot5', 'volume1-snapshot5', 'volume3-snapshot5', 'volume4-snapshot5']
attached:['volume2', 'volume3', 'volume4']
Detached:['volume1']
Deleted:['volume2-snapshot5', 'volume3-snapshot1', 'vm1-snapshot10', 'volume1-snapshot10', 'volume2-snapshot10', 'volume3-snapshot10', 'volume4-snapshot10']
Expunged:[]
Ha:[]
Group:
'''