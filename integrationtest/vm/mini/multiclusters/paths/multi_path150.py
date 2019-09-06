import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", checking_point=1, faild_point=100000, path_list=[
		[TestAction.create_mini_vm, 'vm1', 'data_volume=true', 'cluster=cluster2'],
		[TestAction.create_mini_vm, 'vm2', 'cluster=cluster1'],
		[TestAction.create_vm_backup, 'vm2', 'vm2-backup1'],
		[TestAction.create_mini_vm, 'vm3', 'cluster=cluster2', 'flag=thin'],
		[TestAction.resize_volume, 'vm3', 5*1024*1024],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.create_volume, 'volume2', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.attach_volume, 'vm1', 'volume2'],
		[TestAction.detach_volume, 'volume2'],
		[TestAction.create_volume, 'volume3', 'cluster=cluster2', 'flag=thick,scsi'],
		[TestAction.add_image, 'image1', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.use_vm_backup, 'vm2-backup1'],
		[TestAction.delete_image, 'image1'],
		[TestAction.recover_image, 'image1'],
		[TestAction.delete_image, 'image1'],
		[TestAction.expunge_image, 'image1'],
		[TestAction.attach_volume, 'vm1', 'volume2'],
		[TestAction.create_volume_backup, 'volume2', 'volume2-backup2'],
		[TestAction.detach_volume, 'volume2'],
		[TestAction.create_mini_vm, 'vm4', 'data_volume=true', 'cluster=cluster2'],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.create_image_from_volume, 'vm1', 'vm1-image2'],
		[TestAction.create_volume, 'volume5', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.attach_volume, 'vm2', 'volume5'],
		[TestAction.create_volume, 'volume6', 'cluster=cluster2', 'flag=thick,scsi'],
		[TestAction.attach_volume, 'vm3', 'volume2'],
		[TestAction.use_volume_backup, 'volume2-backup2'],
		[TestAction.detach_volume, 'volume2'],
		[TestAction.start_vm, 'vm4'],
		[TestAction.delete_volume, 'volume5'],
		[TestAction.expunge_volume, 'volume5'],
		[TestAction.start_vm, 'vm3'],
		[TestAction.reboot_vm, 'vm3'],
		[TestAction.attach_volume, 'vm4', 'volume6'],
		[TestAction.create_volume_backup, 'volume6', 'volume6-backup3'],
		[TestAction.detach_volume, 'volume6'],
		[TestAction.create_image_from_volume, 'vm2', 'vm2-image3'],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.delete_vm_backup, 'vm2-backup1'],
])




'''
The final status:
Running:['vm4', 'vm3']
Stopped:['vm2', 'vm1']
Enadbled:['volume2-backup2', 'volume6-backup3', 'vm1-image2', 'vm2-image3']
attached:['auto-volume1', 'auto-volume4']
Detached:['volume3', 'volume2', 'volume6']
Deleted:['vm2-backup1']
Expunged:['volume5', 'image1']
Ha:[]
Group:
'''