import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", checking_point=1, faild_point=100000, path_list=[
		[TestAction.create_mini_vm, 'vm1', 'cluster=cluster2'],
		[TestAction.reboot_vm, 'vm1'],
		[TestAction.create_mini_vm, 'vm2', 'cluster=cluster1'],
		[TestAction.create_volume, 'volume1', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.attach_volume, 'vm2', 'volume1'],
		[TestAction.create_volume_backup, 'volume1', 'volume1-backup1'],
		[TestAction.create_mini_vm, 'vm3', 'cluster=cluster2'],
		[TestAction.stop_vm, 'vm3'],
		[TestAction.start_vm, 'vm3'],
		[TestAction.resize_data_volume, 'volume1', 5*1024*1024],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.create_volume, 'volume2', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.attach_volume, 'vm3', 'volume2'],
		[TestAction.detach_volume, 'volume2'],
		[TestAction.delete_volume, 'volume2'],
		[TestAction.add_image, 'image1', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.create_volume, 'volume3', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.attach_volume, 'vm3', 'volume3'],
		[TestAction.start_vm, 'vm3'],
		[TestAction.create_volume_backup, 'volume3', 'volume3-backup2'],
		[TestAction.stop_vm, 'vm3'],
		[TestAction.delete_volume_backup, 'volume3-backup2'],
		[TestAction.delete_image, 'image1'],
		[TestAction.expunge_image, 'image1'],
		[TestAction.create_vm_backup, 'vm2', 'vm2-backup3'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.reboot_vm, 'vm1'],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.create_image_from_volume, 'vm2', 'vm2-image2'],
		[TestAction.create_volume, 'volume4', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.attach_volume, 'vm2', 'volume4'],
		[TestAction.delete_volume, 'volume4'],
		[TestAction.recover_volume, 'volume4'],
		[TestAction.create_volume, 'volume5', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.attach_volume, 'vm1', 'volume5'],
		[TestAction.create_volume_backup, 'volume5', 'volume5-backup5'],
		[TestAction.delete_volume_backup, 'volume5-backup5'],
		[TestAction.destroy_vm, 'vm2'],
		[TestAction.expunge_vm, 'vm2'],
		[TestAction.delete_volume, 'volume1'],
		[TestAction.expunge_volume, 'volume1'],
		[TestAction.create_mini_vm, 'vm4', 'data_volume=true', 'cluster=cluster2'],
		[TestAction.create_mini_vm, 'vm5', 'cluster=cluster1'],
		[TestAction.attach_volume, 'vm5', 'volume4'],
		[TestAction.create_volume_backup, 'volume4', 'volume4-backup6'],
		[TestAction.create_image_from_volume, 'vm4', 'vm4-image3'],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.create_vm_backup, 'vm1', 'vm1-backup7'],
		[TestAction.delete_vm_backup, 'vm1-backup7'],
		[TestAction.stop_vm, 'vm1'],
])




'''
The final status:
Running:['vm5']
Stopped:['vm3', 'vm4', 'vm1']
Enadbled:['volume1-backup1', 'vm2-backup3', 'volume1-backup3', 'volume4-backup6', 'vm2-image2', 'vm4-image3']
attached:['volume3', 'volume5', 'auto-volume4', 'volume4']
Detached:[]
Deleted:['volume2', 'volume3-backup2', 'volume5-backup5', 'vm1-backup7', 'volume5-backup7']
Expunged:['vm2', 'volume1', 'image1']
Ha:[]
Group:
	vm_backup1:['vm2-backup3', 'volume1-backup3']---vm2@volume1
'''