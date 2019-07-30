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
		[TestAction.reboot_vm, 'vm1'],
		[TestAction.create_volume_backup, 'volume1', 'volume1-backup1'],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot5'],
		[TestAction.batch_delete_volume_snapshot, ['volume1-snapshot5','volume2-snapshot1',]],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot9'],
		[TestAction.clone_vm, 'vm1', 'vm2', 'full'],
		[TestAction.create_volume, 'volume7', 'flag=scsi'],
		[TestAction.attach_volume, 'vm1', 'volume7'],
		[TestAction.stop_vm, 'vm2'],
		[TestAction.reinit_vm, 'vm2'],
		[TestAction.delete_vm_snapshot, 'vm1-snapshot9'],
])



'''
The final status:
Running:['vm1']
Stopped:['vm2']
Enadbled:['vm1-snapshot1', 'volume1-snapshot1', 'volume3-snapshot1', 'vm1-snapshot5', 'volume2-snapshot5', 'volume3-snapshot5', 'volume1-backup1']
attached:['volume1', 'volume2', 'volume3', 'volume4', 'volume5', 'volume6', 'volume7']
Detached:[]
Deleted:['volume1-snapshot5', 'volume2-snapshot1', 'vm1-snapshot9', 'volume1-snapshot9', 'volume2-snapshot9', 'volume3-snapshot9']
Expunged:[]
Ha:[]
Group:
'''