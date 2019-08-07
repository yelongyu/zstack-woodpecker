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
		[TestAction.resize_volume, 'vm1', 5*1024*1024],
		[TestAction.detach_volume, 'volume2'],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot5'],
		[TestAction.delete_vm_snapshot, 'vm1-snapshot1'],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot8'],
		[TestAction.clone_vm, 'vm1', 'vm2'],
		[TestAction.create_volume_backup, 'volume1', 'volume1-backup1'],
		[TestAction.migrate_vm, 'vm1'],
		[TestAction.delete_vm_snapshot, 'vm1-snapshot5'],
])



'''
The final status:
Running:['vm1', 'vm2']
Stopped:[]
Enadbled:['vm1-snapshot8', 'volume1-snapshot8', 'volume3-snapshot8', 'volume1-backup1']
attached:['volume1', 'volume3']
Detached:['volume2']
Deleted:['vm1-snapshot1', 'volume1-snapshot1', 'volume2-snapshot1', 'volume3-snapshot1', 'vm1-snapshot5', 'volume1-snapshot5', 'volume3-snapshot5']
Expunged:[]
Ha:[]
Group:
	vm_snap3:['vm1-snapshot8', 'volume1-snapshot8', 'volume3-snapshot8']---vm1@volume1_volume3
'''