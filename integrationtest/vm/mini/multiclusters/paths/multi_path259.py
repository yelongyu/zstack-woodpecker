import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", checking_point=1, faild_point=100000, path_list=[
		[TestAction.create_mini_vm, 'vm1', 'data_volume=true', 'cluster=cluster2'],
		[TestAction.create_mini_vm, 'vm2', 'cluster=cluster1'],
		[TestAction.create_vm_backup, 'vm2', 'vm2-backup1'],
		[TestAction.start_vm, 'vm2'],
		[TestAction.stop_vm, 'vm2'],
		[TestAction.create_volume, 'volume2', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.resize_data_volume, 'volume2', 5*1024*1024],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.create_volume, 'volume3', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.attach_volume, 'vm1', 'volume3'],
		[TestAction.detach_volume, 'volume3'],
		[TestAction.create_volume, 'volume4', 'cluster=cluster1', 'flag=thick,scsi'],
		[TestAction.add_image, 'image1', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.attach_volume, 'vm1', 'volume4'],
		[TestAction.create_volume_backup, 'volume4', 'volume4-backup2'],
		[TestAction.delete_volume_backup, 'volume4-backup2'],
		[TestAction.detach_volume, 'volume4'],
		[TestAction.delete_image, 'image1'],
		[TestAction.expunge_image, 'image1'],
		[TestAction.create_volume_backup, 'auto-volume1', 'auto-volume1-backup3'],
		[TestAction.destroy_vm, 'vm1'],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.create_mini_vm, 'vm3', 'cluster=cluster2'],
		[TestAction.migrate_vm, 'vm3'],
		[TestAction.create_volume, 'volume5', 'size=random', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.create_volume, 'volume6', 'cluster=cluster1', 'flag=thick,scsi'],
		[TestAction.use_vm_backup, 'vm2-backup1'],
		[TestAction.destroy_vm, 'vm2'],
		[TestAction.expunge_vm, 'vm2'],
		[TestAction.delete_volume, 'volume3'],
		[TestAction.expunge_volume, 'volume3'],
		[TestAction.recover_vm, 'vm1'],
		[TestAction.attach_volume, 'vm1', 'volume2'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.create_volume_backup, 'volume2', 'volume2-backup4'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.detach_volume, 'volume2'],
		[TestAction.create_mini_vm, 'vm4', 'cluster=cluster1'],
		[TestAction.migrate_vm, 'vm4'],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.attach_volume, 'vm1', 'volume2'],
		[TestAction.use_volume_backup, 'volume2-backup4'],
		[TestAction.detach_volume, 'volume2'],
])




'''
The final status:
Running:['vm4']
Stopped:['vm1', 'vm3']
Enadbled:['vm2-backup1', 'auto-volume1-backup3', 'volume2-backup4']
attached:[]
Detached:['volume4', 'auto-volume1', 'volume5', 'volume6', 'volume2']
Deleted:['volume4-backup2']
Expunged:['vm2', 'volume3', 'image1']
Ha:[]
Group:
	vm_backup1:['vm2-backup1']---vm2@
'''