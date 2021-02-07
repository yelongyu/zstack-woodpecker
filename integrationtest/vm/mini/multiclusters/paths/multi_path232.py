import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", checking_point=1, faild_point=100000, path_list=[
		[TestAction.create_mini_vm, 'vm1', 'cluster=cluster2'],
		[TestAction.create_vm_backup, 'vm1', 'vm1-backup1'],
		[TestAction.create_mini_vm, 'vm2', 'cpu=random', 'cluster=cluster2'],
		[TestAction.create_mini_vm, 'vm3', 'cluster=cluster1'],
		[TestAction.resize_volume, 'vm1', 5*1024*1024],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.create_volume, 'volume1', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.attach_volume, 'vm2', 'volume1'],
		[TestAction.detach_volume, 'volume1'],
		[TestAction.create_volume, 'volume2', 'cluster=cluster1', 'flag=thick,scsi'],
		[TestAction.add_image, 'image1', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.attach_volume, 'vm3', 'volume2'],
		[TestAction.create_volume_backup, 'volume2', 'volume2-backup2'],
		[TestAction.stop_vm, 'vm3'],
		[TestAction.use_volume_backup, 'volume2-backup2'],
		[TestAction.start_vm, 'vm3'],
		[TestAction.delete_image, 'image1'],
		[TestAction.expunge_image, 'image1'],
		[TestAction.create_vm_backup, 'vm3', 'vm3-backup3'],
		[TestAction.create_mini_vm, 'vm4', 'cluster=cluster2'],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.resize_volume, 'vm3', 5*1024*1024],
		[TestAction.attach_volume, 'vm2', 'volume1'],
		[TestAction.delete_volume, 'volume2'],
		[TestAction.delete_vm_backup, 'vm1-backup1'],
		[TestAction.create_mini_vm, 'vm5', 'cluster=cluster1', 'flag=thin'],
		[TestAction.expunge_volume, 'volume2'],
		[TestAction.create_mini_vm, 'vm6', 'data_volume=true', 'cluster=cluster1'],
		[TestAction.create_volume, 'volume4', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.attach_volume, 'vm2', 'volume4'],
		[TestAction.start_vm, 'vm2'],
		[TestAction.create_volume_backup, 'volume4', 'volume4-backup5'],
		[TestAction.stop_vm, 'vm2'],
		[TestAction.create_image_from_volume, 'vm3', 'vm3-image2'],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.create_volume, 'volume5', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.attach_volume, 'vm2', 'volume5'],
		[TestAction.start_vm, 'vm2'],
		[TestAction.create_volume_backup, 'volume5', 'volume5-backup6'],
		[TestAction.stop_vm, 'vm2'],
		[TestAction.use_volume_backup, 'volume5-backup6'],
])




'''
The final status:
Running:['vm3', 'vm5', 'vm6']
Stopped:['vm1', 'vm4', 'vm2']
Enadbled:['volume2-backup2', 'vm3-backup3', 'volume2-backup3', 'volume4-backup5', 'volume5-backup6', 'vm3-image2']
attached:['volume1', 'auto-volume6', 'volume4', 'volume5']
Detached:[]
Deleted:['vm1-backup1']
Expunged:['volume2', 'image1']
Ha:[]
Group:
	vm_backup2:['vm3-backup3', 'volume2-backup3']---vm3@volume2
'''