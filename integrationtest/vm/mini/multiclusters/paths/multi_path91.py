import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", checking_point=1, faild_point=100000, path_list=[
		[TestAction.create_mini_vm, 'vm1', 'cluster=cluster2'],
		[TestAction.change_vm_ha, 'vm1'],
		[TestAction.create_vm_backup, 'vm1', 'vm1-backup1'],
		[TestAction.create_mini_vm, 'vm2', 'cluster=cluster1'],
		[TestAction.start_vm, 'vm2'],
		[TestAction.stop_vm, 'vm2'],
		[TestAction.migrate_vm, 'vm1'],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.create_volume, 'volume1', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.attach_volume, 'vm2', 'volume1'],
		[TestAction.detach_volume, 'volume1'],
		[TestAction.delete_volume, 'volume1'],
		[TestAction.add_image, 'image1', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.start_vm, 'vm2'],
		[TestAction.create_vm_backup, 'vm2', 'vm2-backup2'],
		[TestAction.stop_vm, 'vm2'],
		[TestAction.use_vm_backup, 'vm2-backup2'],
		[TestAction.delete_image, 'image1'],
		[TestAction.expunge_image, 'image1'],
		[TestAction.start_vm, 'vm2'],
		[TestAction.create_vm_backup, 'vm2', 'vm2-backup3'],
		[TestAction.stop_vm, 'vm2'],
		[TestAction.create_mini_vm, 'vm3', 'data_volume=true', 'cluster=cluster2'],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.resize_volume, 'vm3', 5*1024*1024],
		[TestAction.create_volume, 'volume3', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.attach_volume, 'vm1', 'volume3'],
		[TestAction.detach_volume, 'volume3'],
		[TestAction.recover_volume, 'volume1'],
		[TestAction.use_vm_backup, 'vm2-backup2'],
		[TestAction.create_mini_vm, 'vm4', 'network=random', 'cluster=cluster2'],
		[TestAction.delete_volume, 'volume1'],
		[TestAction.expunge_volume, 'volume1'],
		[TestAction.create_mini_vm, 'vm5', 'data_volume=true', 'cluster=cluster1'],
		[TestAction.create_volume, 'volume5', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.attach_volume, 'vm2', 'volume5'],
		[TestAction.start_vm, 'vm2'],
		[TestAction.create_volume_backup, 'volume5', 'volume5-backup4'],
		[TestAction.stop_vm, 'vm2'],
		[TestAction.create_image_from_volume, 'vm3', 'vm3-image2'],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.create_volume, 'volume6', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.attach_volume, 'vm5', 'volume6'],
		[TestAction.start_vm, 'vm5'],
		[TestAction.create_volume_backup, 'volume6', 'volume6-backup5'],
		[TestAction.stop_vm, 'vm5'],
		[TestAction.delete_volume_backup, 'volume6-backup5'],
])




'''
The final status:
Running:['vm1', 'vm3', 'vm4']
Stopped:['vm2', 'vm5']
Enadbled:['vm1-backup1', 'vm2-backup2', 'vm2-backup3', 'volume5-backup4', 'vm3-image2']
attached:['auto-volume3', 'auto-volume5', 'volume5', 'volume6']
Detached:['volume3']
Deleted:['volume6-backup5']
Expunged:['volume1', 'image1']
Ha:['vm1']
Group:
	vm_backup2:['vm2-backup2']---vm2@
	vm_backup3:['vm2-backup3']---vm2@
	vm_backup1:['vm1-backup1']---vm1@
'''