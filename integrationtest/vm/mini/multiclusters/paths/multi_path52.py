import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", checking_point=1, faild_point=100000, path_list=[
		[TestAction.create_mini_vm, 'vm1', 'cluster=cluster2'],
		[TestAction.destroy_vm, 'vm1'],
		[TestAction.create_mini_vm, 'vm2', 'cluster=cluster2'],
		[TestAction.create_vm_backup, 'vm2', 'vm2-backup1'],
		[TestAction.create_mini_vm, 'vm3', 'cpu=random', 'cluster=cluster2'],
		[TestAction.create_mini_vm, 'vm4', 'cluster=cluster1'],
		[TestAction.create_image_from_volume, 'vm4', 'vm4-image1'],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.create_volume, 'volume1', 'size=random', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.create_volume, 'volume2', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.delete_volume, 'volume2'],
		[TestAction.add_image, 'image2', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.recover_volume, 'volume2'],
		[TestAction.attach_volume, 'vm2', 'volume2'],
		[TestAction.create_volume_backup, 'volume2', 'volume2-backup2'],
		[TestAction.delete_volume_backup, 'volume2-backup2'],
		[TestAction.detach_volume, 'volume2'],
		[TestAction.delete_image, 'vm4-image1'],
		[TestAction.recover_image, 'vm4-image1'],
		[TestAction.delete_image, 'image2'],
		[TestAction.expunge_image, 'image2'],
		[TestAction.start_vm, 'vm4'],
		[TestAction.create_vm_backup, 'vm4', 'vm4-backup3'],
		[TestAction.stop_vm, 'vm4'],
		[TestAction.reboot_vm, 'vm2'],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.create_image_from_volume, 'vm3', 'vm3-image3'],
		[TestAction.attach_volume, 'vm3', 'volume1'],
		[TestAction.create_volume, 'volume3', 'cluster=cluster2', 'flag=thick,scsi'],
		[TestAction.attach_volume, 'vm4', 'volume2'],
		[TestAction.start_vm, 'vm4'],
		[TestAction.create_volume_backup, 'volume2', 'volume2-backup4'],
		[TestAction.delete_volume_backup, 'volume2-backup4'],
		[TestAction.stop_vm, 'vm4'],
		[TestAction.detach_volume, 'volume2'],
		[TestAction.create_mini_vm, 'vm5', 'cluster=cluster2', 'flag=thin'],
		[TestAction.delete_volume, 'volume1'],
		[TestAction.expunge_volume, 'volume1'],
		[TestAction.start_vm, 'vm4'],
		[TestAction.reboot_vm, 'vm4'],
		[TestAction.create_vm_backup, 'vm5', 'vm5-backup5'],
		[TestAction.resize_data_volume, 'volume2', 5*1024*1024],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.delete_vm_backup, 'vm4-backup3'],
])




'''
The final status:
Running:['vm4']
Stopped:['vm2', 'vm3', 'vm5']
Enadbled:['vm2-backup1', 'vm5-backup5', 'vm4-image1', 'vm3-image3']
attached:[]
Detached:['volume3', 'volume2']
Deleted:['vm1', 'volume2-backup2', 'volume2-backup4', 'vm4-backup3']
Expunged:['volume1', 'image2']
Ha:[]
Group:
	vm_backup3:['vm5-backup5']---vm5@
	vm_backup1:['vm2-backup1']---vm2@
'''