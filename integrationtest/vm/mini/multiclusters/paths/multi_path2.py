import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", checking_point=1, faild_point=100000, path_list=[
		[TestAction.create_mini_vm, 'vm1', 'cluster=cluster1'],
		[TestAction.destroy_vm, 'vm1'],
		[TestAction.recover_vm, 'vm1'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.create_vm_backup, 'vm1', 'vm1-backup1'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.create_image_from_volume, 'vm1', 'vm1-image1'],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.create_volume, 'volume1', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.create_mini_vm, 'vm2', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.attach_volume, 'vm2', 'volume1'],
		[TestAction.detach_volume, 'volume1'],
		[TestAction.create_volume, 'volume2', 'cluster=cluster1', 'flag=thick,scsi'],
		[TestAction.add_image, 'image2', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.attach_volume, 'vm1', 'volume1'],
		[TestAction.create_volume_backup, 'volume1', 'volume1-backup2'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.use_volume_backup, 'volume1-backup2'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.detach_volume, 'volume1'],
		[TestAction.delete_image, 'image2'],
		[TestAction.recover_image, 'image2'],
		[TestAction.delete_image, 'image2'],
		[TestAction.expunge_image, 'image2'],
		[TestAction.create_vm_backup, 'vm2', 'vm2-backup3'],
		[TestAction.create_mini_vm, 'vm3', 'data_volume=true', 'cluster=cluster2'],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.create_image_from_volume, 'vm3', 'vm3-image3'],
		[TestAction.attach_volume, 'vm1', 'volume2'],
		[TestAction.detach_volume, 'volume2'],
		[TestAction.delete_volume, 'volume2'],
		[TestAction.attach_volume, 'vm1', 'volume1'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.use_volume_backup, 'volume1-backup2'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.detach_volume, 'volume1'],
		[TestAction.create_mini_vm, 'vm4', 'cluster=cluster1', 'flag=thin'],
		[TestAction.expunge_volume, 'volume2'],
		[TestAction.destroy_vm, 'vm3'],
		[TestAction.recover_vm, 'vm3'],
		[TestAction.attach_volume, 'vm1', 'volume1'],
		[TestAction.create_volume_backup, 'volume1', 'volume1-backup4'],
		[TestAction.detach_volume, 'volume1'],
		[TestAction.resize_volume, 'vm4', 5*1024*1024],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.delete_volume_backup, 'volume1-backup2'],
])




'''
The final status:
Running:[]
Stopped:['vm2', 'vm3', 'vm1', 'vm4']
Enadbled:['vm1-backup1', 'vm2-backup3', 'volume1-backup4', 'vm1-image1', 'vm3-image3']
attached:[]
Detached:['auto-volume3', 'volume1']
Deleted:['volume1-backup2']
Expunged:['volume2', 'image2']
Ha:[]
Group:
	vm_backup2:['vm2-backup3']---vm2@
	vm_backup1:['vm1-backup1']---vm1@
'''