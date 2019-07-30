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
		[TestAction.migrate_vm, 'vm1'],
		[TestAction.create_volume_snapshot, 'volume1', 'volume1-snapshot5'],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot6'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.change_vm_image, 'vm1'],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot10'],
		[TestAction.use_volume_snapshot, 'vm1-snapshot6'],
		[TestAction.migrate_volume, 'volume1'],
		[TestAction.ps_migrate_vm, 'vm1'],
		[TestAction.delete_vm_snapshot, 'vm1-snapshot1'],
])



'''
The final status:
Running:[]
Stopped:['vm1']
Enadbled:['volume1-snapshot5', 'vm1-snapshot6', 'volume1-snapshot6', 'volume2-snapshot6', 'volume3-snapshot6', 'vm1-snapshot10', 'volume1-snapshot10', 'volume2-snapshot10', 'volume3-snapshot10']
attached:['volume1', 'volume2', 'volume3']
Detached:[]
Deleted:['vm1-snapshot1', 'volume1-snapshot1', 'volume2-snapshot1', 'volume3-snapshot1']
Expunged:[]
Ha:[]
Group:
	vm_snap2:['vm1-snapshot6', 'volume1-snapshot6', 'volume2-snapshot6', 'volume3-snapshot6']---vm1volume1_volume2_volume3
	vm_snap3:['vm1-snapshot10', 'volume1-snapshot10', 'volume2-snapshot10', 'volume3-snapshot10']---vm1volume1_volume2_volume3
'''