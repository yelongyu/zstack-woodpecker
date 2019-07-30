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
		[TestAction.create_vm_backup, 'vm1', 'vm1-backup1'],
		[TestAction.create_volume_snapshot, 'volume2', 'volume2-snapshot5'],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot6'],
		[TestAction.create_volume_backup, 'vm1-root', 'vm1-root-backup5'],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot10'],
		[TestAction.clone_vm, 'vm1', 'vm2', 'full'],
		[TestAction.create_volume_snapshot, 'volume3', 'volume3-snapshot14'],
		[TestAction.reboot_vm, 'vm1'],
		[TestAction.delete_vm_snapshot, 'vm1-snapshot1'],
])



'''
The final status:
Running:['vm1', 'vm2']
Stopped:[]
Enadbled:['volume2-snapshot5', 'vm1-snapshot6', 'volume1-snapshot6', 'volume2-snapshot6', 'volume3-snapshot6', 'vm1-snapshot10', 'volume1-snapshot10', 'volume2-snapshot10', 'volume3-snapshot10', 'volume3-snapshot14', 'vm1-backup1', 'volume1-backup1', 'volume2-backup1', 'volume3-backup1', 'vm1-root-backup5']
attached:['volume1', 'volume2', 'volume3', 'volume4', 'volume5', 'volume6']
Detached:[]
Deleted:['vm1-snapshot1', 'volume1-snapshot1', 'volume2-snapshot1', 'volume3-snapshot1']
Expunged:[]
Ha:[]
Group:
	vm_snap2:['vm1-snapshot6', 'volume1-snapshot6', 'volume2-snapshot6', 'volume3-snapshot6']---vm1volume1_volume2_volume3
	vm_snap3:['vm1-snapshot10', 'volume1-snapshot10', 'volume2-snapshot10', 'volume3-snapshot10']---vm1volume1_volume2_volume3
	vm_backup1:['vm1-backup1', 'volume1-backup1', 'volume2-backup1', 'volume3-backup1']---vm1_volume1_volume2_volume3
'''