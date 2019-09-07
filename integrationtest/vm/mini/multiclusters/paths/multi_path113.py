import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", checking_point=1, faild_point=100000, path_list=[
		[TestAction.create_mini_vm, 'vm1', 'data_volume=true', 'cluster=cluster2'],
		[TestAction.create_mini_vm, 'vm2', 'cluster=cluster1'],
		[TestAction.create_vm_backup, 'vm2', 'vm2-backup1'],
		[TestAction.create_mini_vm, 'vm3', 'cluster=cluster1', 'flag=thick'],
		[TestAction.migrate_vm, 'vm1'],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.create_volume, 'volume2', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.attach_volume, 'vm3', 'volume2'],
		[TestAction.detach_volume, 'volume2'],
		[TestAction.create_volume, 'volume3', 'cluster=cluster2', 'flag=thick,scsi'],
		[TestAction.add_image, 'image1', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.use_vm_backup, 'vm2-backup1'],
		[TestAction.delete_image, 'image1'],
		[TestAction.expunge_image, 'image1'],
		[TestAction.create_volume_backup, 'auto-volume1', 'auto-volume1-backup2'],
		[TestAction.create_mini_vm, 'vm4', 'data_volume=true', 'cluster=cluster1'],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.start_vm, 'vm3'],
		[TestAction.migrate_vm, 'vm3'],
		[TestAction.create_volume, 'volume5', 'size=random', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.create_volume, 'volume6', 'cluster=cluster2', 'flag=thin,scsi'],
		[TestAction.delete_volume_backup, 'auto-volume1-backup2'],
		[TestAction.create_mini_vm, 'vm5', 'cluster=cluster1', 'flag=thin'],
		[TestAction.delete_volume, 'volume6'],
		[TestAction.expunge_volume, 'volume6'],
		[TestAction.create_mini_vm, 'vm6', 'data_volume=true', 'cluster=cluster2'],
		[TestAction.create_vm_backup, 'vm1', 'vm1-backup3'],
		[TestAction.migrate_vm, 'vm5'],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.delete_vm_backup, 'vm2-backup1'],
])




'''
The final status:
Running:['vm1', 'vm6']
Stopped:['vm2', 'vm4', 'vm3', 'vm5']
Enadbled:['vm1-backup3', 'auto-volume1-backup3']
attached:['auto-volume1', 'auto-volume4', 'auto-volume6']
Detached:['volume2', 'volume3', 'volume5']
Deleted:['auto-volume1-backup2', 'vm2-backup1']
Expunged:['volume6', 'image1']
Ha:[]
Group:
	vm_backup2:['vm1-backup3', 'auto-volume1-backup3']---vm1@auto-volume1
'''