import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", checking_point=8, faild_point=13, path_list=[
		[TestAction.create_vm, 'vm1', ],
		[TestAction.create_volume, 'volume1', 'flag=scsi'],
		[TestAction.attach_volume, 'vm1', 'volume1'],
		[TestAction.create_volume, 'volume2', 'flag=scsi'],
		[TestAction.attach_volume, 'vm1', 'volume2'],
		[TestAction.create_volume, 'volume3', 'flag=scsi'],
		[TestAction.attach_volume, 'vm1', 'volume3'],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot1'],
		[TestAction.create_vm_backup, 'vm1', 'vm1-backup1'],
		[TestAction.create_vm, 'vm2', ],
		[TestAction.delete_volume, 'volume3'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.delete_vm_snapshot, 'vm1-snapshot1'],
])




'''
The final status:
Running:['vm2']
Stopped:['vm1']
Enadbled:['vm1-backup1', 'volume1-backup1', 'volume2-backup1', 'volume3-backup1']
attached:['volume1', 'volume2']
Detached:[]
Deleted:['volume3', 'vm1-snapshot1', 'volume1-snapshot1', 'volume2-snapshot1', 'volume3-snapshot1']
Expunged:[]
Ha:[]
Group:
	vm_backup1:['vm1-backup1', 'volume1-backup1', 'volume2-backup1', 'volume3-backup1']---vm1@volume1_volume2_volume3
'''