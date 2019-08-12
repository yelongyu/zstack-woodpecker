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
		[TestAction.clone_vm, 'vm1', 'vm2'],
		[TestAction.detach_volume, 'volume1'],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot5'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.ps_migrate_vm, 'vm1'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot8'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.ps_migrate_vm, 'vm1'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.create_volume, 'volume4', 'flag=ceph,scsi'],
		[TestAction.attach_volume, 'vm2', 'volume4'],
		[TestAction.create_vm_backup, 'vm1', 'vm1-backup1'],
		[TestAction.delete_vm_snapshot, 'vm1-snapshot1'],
])



'''
The final status:
Running:['vm2', 'vm1']
Stopped:[]
Enadbled:['vm1-snapshot5', 'volume2-snapshot5', 'volume3-snapshot5', 'vm1-snapshot8', 'volume2-snapshot8', 'volume3-snapshot8', 'vm1-backup1', 'volume2-backup1', 'volume3-backup1']
attached:['volume2', 'volume3', 'volume4']
Detached:['volume1']
Deleted:['vm1-snapshot1', 'volume1-snapshot1', 'volume2-snapshot1', 'volume3-snapshot1']
Expunged:[]
Ha:[]
Group:
	vm_snap2:['vm1-snapshot5', 'volume2-snapshot5', 'volume3-snapshot5']---vm1@volume2_volume3
	vm_snap3:['vm1-snapshot8', 'volume2-snapshot8', 'volume3-snapshot8']---vm1@volume2_volume3
	vm_backup1:['vm1-backup1', 'volume2-backup1', 'volume3-backup1']---vm1@volume2_volume3
'''