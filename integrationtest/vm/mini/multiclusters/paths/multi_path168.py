import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", checking_point=1, faild_point=100000, path_list=[
		[TestAction.create_mini_vm, 'vm1', 'data_volume=true', 'cluster=cluster1'],
		[TestAction.create_volume_backup, 'auto-volume1', 'auto-volume1-backup1'],
		[TestAction.create_mini_vm, 'vm2', 'cluster=cluster2', 'flag=thin'],
		[TestAction.create_image_from_volume, 'vm1', 'vm1-image1'],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.create_volume, 'volume2', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.attach_volume, 'vm1', 'volume2'],
		[TestAction.create_volume, 'volume3', 'cluster=cluster2', 'flag=thin,scsi'],
		[TestAction.add_image, 'image2', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.delete_volume_backup, 'auto-volume1-backup1'],
		[TestAction.delete_image, 'image2'],
		[TestAction.recover_image, 'image2'],
		[TestAction.delete_image, 'image2'],
		[TestAction.expunge_image, 'image2'],
		[TestAction.start_vm, 'vm2'],
		[TestAction.create_vm_backup, 'vm2', 'vm2-backup2'],
		[TestAction.stop_vm, 'vm2'],
		[TestAction.change_vm_ha, 'vm1'],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.resize_volume, 'vm2', 5*1024*1024],
		[TestAction.attach_volume, 'vm2', 'volume3'],
		[TestAction.detach_volume, 'volume3'],
		[TestAction.delete_volume, 'volume3'],
		[TestAction.create_volume_backup, 'auto-volume1', 'auto-volume1-backup3'],
		[TestAction.delete_volume_backup, 'auto-volume1-backup3'],
		[TestAction.create_mini_vm, 'vm3', 'cluster=cluster1', 'flag=thin'],
		[TestAction.expunge_volume, 'volume3'],
		[TestAction.create_mini_vm, 'vm4', 'cluster=cluster1'],
		[TestAction.start_vm, 'vm2'],
		[TestAction.create_vm_backup, 'vm2', 'vm2-backup4'],
		[TestAction.stop_vm, 'vm2'],
		[TestAction.create_volume, 'volume4', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.resize_data_volume, 'volume4', 5*1024*1024],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.delete_vm_backup, 'vm2-backup2'],
])




'''
The final status:
Running:['vm1']
Stopped:['vm2', 'vm3', 'vm4']
Enadbled:['vm2-backup4', 'vm1-image1']
attached:['auto-volume1', 'volume2']
Detached:['volume4']
Deleted:['auto-volume1-backup1', 'auto-volume1-backup3', 'vm2-backup2']
Expunged:['volume3', 'image2']
Ha:['vm1']
Group:
	vm_backup2:['vm2-backup4']---vm2@
'''