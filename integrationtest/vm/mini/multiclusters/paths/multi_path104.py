import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", checking_point=1, faild_point=100000, path_list=[
		[TestAction.create_mini_vm, 'vm1', 'cluster=cluster2'],
		[TestAction.change_vm_ha, 'vm1'],
		[TestAction.create_volume, 'volume1', 'flag=scsi'],
		[TestAction.attach_volume, 'vm1', 'volume1'],
		[TestAction.create_volume_backup, 'volume1', 'volume1-backup1'],
		[TestAction.detach_volume, 'volume1'],
		[TestAction.create_mini_vm, 'vm2', 'memory=random', 'cluster=cluster1'],
		[TestAction.migrate_vm, 'vm2'],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.create_volume, 'volume2', 'size=random', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.create_volume, 'volume3', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.delete_volume, 'volume3'],
		[TestAction.recover_volume, 'volume3'],
		[TestAction.add_image, 'image1', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.attach_volume, 'vm2', 'volume1'],
		[TestAction.stop_vm, 'vm2'],
		[TestAction.use_volume_backup, 'volume1-backup1'],
		[TestAction.start_vm, 'vm2'],
		[TestAction.detach_volume, 'volume1'],
		[TestAction.delete_image, 'image1'],
		[TestAction.recover_image, 'image1'],
		[TestAction.delete_image, 'image1'],
		[TestAction.expunge_image, 'image1'],
		[TestAction.create_vm_backup, 'vm2', 'vm2-backup2'],
		[TestAction.create_mini_vm, 'vm3', 'data_volume=true', 'cluster=cluster1'],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.create_image_from_volume, 'vm3', 'vm3-image2'],
		[TestAction.create_volume, 'volume5', 'size=random', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.delete_volume, 'volume2'],
		[TestAction.stop_vm, 'vm2'],
		[TestAction.use_vm_backup, 'vm2-backup2'],
		[TestAction.start_vm, 'vm2'],
		[TestAction.create_mini_vm, 'vm4', 'memory=random', 'cluster=cluster2'],
		[TestAction.delete_volume, 'volume5'],
		[TestAction.expunge_volume, 'volume5'],
		[TestAction.change_vm_ha, 'vm1'],
		[TestAction.create_vm_backup, 'vm1', 'vm1-backup3'],
		[TestAction.create_volume, 'volume6', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.resize_data_volume, 'volume6', 5*1024*1024],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.delete_vm_backup, 'vm2-backup2'],
])




'''
The final status:
Running:['vm1', 'vm3', 'vm2', 'vm4']
Stopped:[]
Enadbled:['volume1-backup1', 'vm1-backup3', 'vm3-image2']
attached:['auto-volume3']
Detached:['volume3', 'volume1', 'volume6']
Deleted:['volume2', 'vm2-backup2']
Expunged:['volume5', 'image1']
Ha:[]
Group:
	vm_backup2:['vm1-backup3']---vm1@
'''