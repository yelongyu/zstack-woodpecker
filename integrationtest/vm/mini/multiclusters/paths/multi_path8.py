import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", checking_point=1, faild_point=100000, path_list=[
		[TestAction.create_mini_vm, 'vm1', 'cluster=cluster2'],
		[TestAction.destroy_vm, 'vm1'],
		[TestAction.recover_vm, 'vm1'],
		[TestAction.create_volume, 'volume1', 'flag=scsi'],
		[TestAction.attach_volume, 'vm1', 'volume1'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.create_volume_backup, 'volume1', 'volume1-backup1'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.detach_volume, 'volume1'],
		[TestAction.create_mini_vm, 'vm2', 'cluster=cluster2', 'flag=thick'],
		[TestAction.create_image_from_volume, 'vm2', 'vm2-image1'],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.create_volume, 'volume2', 'size=random', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.create_volume, 'volume3', 'cluster=cluster2', 'flag=thick,scsi'],
		[TestAction.add_image, 'image2', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.attach_volume, 'vm2', 'volume1'],
		[TestAction.stop_vm, 'vm2'],
		[TestAction.use_volume_backup, 'volume1-backup1'],
		[TestAction.start_vm, 'vm2'],
		[TestAction.detach_volume, 'volume1'],
		[TestAction.delete_image, 'image2'],
		[TestAction.delete_image, 'vm2-image1'],
		[TestAction.expunge_image, 'vm2-image1'],
		[TestAction.create_vm_backup, 'vm2', 'vm2-backup2'],
		[TestAction.destroy_vm, 'vm1'],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.create_mini_vm, 'vm3', 'cluster=cluster1'],
		[TestAction.create_image_from_volume, 'vm3', 'vm3-image3'],
		[TestAction.attach_volume, 'vm2', 'volume3'],
		[TestAction.create_volume, 'volume4', 'cluster=cluster2', 'flag=thick,scsi'],
		[TestAction.delete_volume_backup, 'volume1-backup1'],
		[TestAction.start_vm, 'vm3'],
		[TestAction.stop_vm, 'vm3'],
		[TestAction.delete_volume, 'volume2'],
		[TestAction.expunge_volume, 'volume2'],
		[TestAction.create_mini_vm, 'vm4', 'data_volume=true', 'cluster=cluster2'],
		[TestAction.start_vm, 'vm3'],
		[TestAction.create_vm_backup, 'vm3', 'vm3-backup3'],
		[TestAction.stop_vm, 'vm3'],
		[TestAction.create_image_from_volume, 'vm3', 'vm3-image4'],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.attach_volume, 'vm4', 'volume4'],
		[TestAction.create_volume_backup, 'volume4', 'volume4-backup4'],
		[TestAction.stop_vm, 'vm4'],
		[TestAction.use_volume_backup, 'volume4-backup4'],
		[TestAction.start_vm, 'vm4'],
		[TestAction.detach_volume, 'volume4'],
])




'''
The final status:
Running:['vm4']
Stopped:['vm2', 'vm3']
Enadbled:['vm2-backup2', 'vm3-backup3', 'volume4-backup4', 'vm3-image3', 'vm3-image4']
attached:['volume3', 'auto-volume4']
Detached:['volume1', 'volume4']
Deleted:['vm1', 'volume1-backup1', 'image2']
Expunged:['volume2', 'vm2-image1']
Ha:[]
Group:
	vm_backup2:['vm3-backup3']---vm3@
	vm_backup1:['vm2-backup2']---vm2@
'''