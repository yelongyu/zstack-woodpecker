import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", checking_point=1, faild_point=100000, path_list=[
		[TestAction.create_mini_vm, 'vm1', 'cluster=cluster1'],
		[TestAction.destroy_vm, 'vm1'],
		[TestAction.create_mini_vm, 'vm2', 'cluster=cluster1'],
		[TestAction.create_vm_backup, 'vm2', 'vm2-backup1'],
		[TestAction.start_vm, 'vm2'],
		[TestAction.stop_vm, 'vm2'],
		[TestAction.resize_volume, 'vm2', 5*1024*1024],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.create_mini_vm, 'vm3', 'cluster=cluster2'],
		[TestAction.create_volume, 'volume1', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.attach_volume, 'vm3', 'volume1'],
		[TestAction.create_volume, 'volume2', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.delete_volume, 'volume2'],
		[TestAction.add_image, 'image1', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.use_vm_backup, 'vm2-backup1'],
		[TestAction.delete_image, 'image1'],
		[TestAction.recover_image, 'image1'],
		[TestAction.delete_image, 'image1'],
		[TestAction.expunge_image, 'image1'],
		[TestAction.create_volume_backup, 'volume1', 'volume1-backup2'],
		[TestAction.create_mini_vm, 'vm4', 'data_volume=true', 'cluster=cluster1'],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.migrate_vm, 'vm4'],
		[TestAction.create_volume, 'volume4', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.attach_volume, 'vm3', 'volume4'],
		[TestAction.create_volume, 'volume5', 'cluster=cluster2', 'flag=thin,scsi'],
		[TestAction.delete_volume_backup, 'volume1-backup2'],
		[TestAction.start_vm, 'vm2'],
		[TestAction.stop_vm, 'vm2'],
		[TestAction.delete_volume, 'volume5'],
		[TestAction.expunge_volume, 'volume5'],
		[TestAction.create_mini_vm, 'vm5', 'data_volume=true', 'cluster=cluster1'],
		[TestAction.start_vm, 'vm3'],
		[TestAction.create_volume_backup, 'volume4', 'volume4-backup3'],
		[TestAction.stop_vm, 'vm3'],
		[TestAction.resize_volume, 'vm4', 5*1024*1024],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.use_vm_backup, 'vm2-backup1'],
])




'''
The final status:
Running:[]
Stopped:['vm5', 'vm4', 'vm3', 'vm2']
Enadbled:['vm2-backup1', 'volume4-backup3']
attached:['volume1', 'auto-volume4', 'volume4', 'auto-volume5']
Detached:[]
Deleted:['vm1', 'volume2', 'volume1-backup2']
Expunged:['volume5', 'image1']
Ha:[]
Group:
	vm_backup1:['vm2-backup1']---vm2@
'''