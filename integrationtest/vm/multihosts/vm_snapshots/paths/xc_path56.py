import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", path_list=[
		[TestAction.create_vm, 'vm1', 'flag=ceph'],
		[TestAction.create_volume, 'volume1', 'flag=ceph,scsi'],
		[TestAction.attach_volume, 'vm1', 'volume1'],
		[TestAction.create_volume, 'volume2', 'flag=ceph,scsi'],
		[TestAction.attach_volume, 'vm1', 'volume2'],
		[TestAction.create_volume, 'volume3', 'flag=ceph,scsi'],
		[TestAction.attach_volume, 'vm1', 'volume3'],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot1'],
		[TestAction.create_volume_snapshot, 'vm1-root', 'vm1-root-snapshot5'],
		[TestAction.create_volume_backup, 'volume1', 'volume1-backup1'],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot6'],
		[TestAction.reboot_vm, 'vm1'],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot10'],
		[TestAction.batch_delete_volume_snapshot, ['vm1-snapshot1','volume1-snapshot6',]],
		[TestAction.delete_volume_snapshot, 'vm1-root-snapshot5'],
		[TestAction.create_vm_backup, 'vm1', 'vm1-backup2'],
		[TestAction.delete_vm_snapshot, 'vm1-snapshot10'],
])



'''
The final status:
Running:['vm1']
Stopped:[]
Enadbled:['volume1-snapshot1', 'volume2-snapshot1', 'volume3-snapshot1', 'vm1-snapshot6', 'volume2-snapshot6', 'volume3-snapshot6', 'volume1-backup1', 'vm1-backup2', 'volume1-backup2', 'volume2-backup2', 'volume3-backup2']
attached:['volume1', 'volume2', 'volume3']
Detached:[]
Deleted:['vm1-snapshot1', 'volume1-snapshot6', 'vm1-root-snapshot5', 'vm1-snapshot10', 'volume1-snapshot10', 'volume2-snapshot10', 'volume3-snapshot10']
Expunged:[]
Ha:[]
Group:
	vm_backup1:['vm1-backup2', 'volume1-backup2', 'volume2-backup2', 'volume3-backup2']---vm1@volume1_volume2_volume3
'''