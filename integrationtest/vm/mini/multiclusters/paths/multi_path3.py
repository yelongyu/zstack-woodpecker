import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", checking_point=1, faild_point=100000, path_list=[
		[TestAction.create_mini_vm, 'vm1', 'cluster=cluster2'],
		[TestAction.reboot_vm, 'vm1'],
		[TestAction.create_volume, 'volume1', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.attach_volume, 'vm1', 'volume1'],
		[TestAction.create_volume_backup, 'volume1', 'volume1-backup1'],
		[TestAction.create_mini_vm, 'vm2', 'cluster=cluster2', 'flag=thin'],
		[TestAction.resize_volume, 'vm2', 5*1024*1024],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.create_volume, 'volume2', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.create_mini_vm, 'vm3', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.attach_volume, 'vm3', 'volume2'],
		[TestAction.detach_volume, 'volume2'],
		[TestAction.delete_volume, 'volume2'],
		[TestAction.recover_volume, 'volume2'],
		[TestAction.add_image, 'image1', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.attach_volume, 'vm3', 'volume2'],
		[TestAction.create_volume_backup, 'volume2', 'volume2-backup2'],
		[TestAction.delete_volume_backup, 'volume2-backup2'],
		[TestAction.delete_image, 'image1'],
		[TestAction.recover_image, 'image1'],
		[TestAction.delete_image, 'image1'],
		[TestAction.expunge_image, 'image1'],
		[TestAction.create_vm_backup, 'vm3', 'vm3-backup3'],
		[TestAction.destroy_vm, 'vm2'],
		[TestAction.recover_vm, 'vm2'],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.start_vm, 'vm2'],
		[TestAction.migrate_vm, 'vm2'],
		[TestAction.create_volume, 'volume3', 'size=random', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.create_volume, 'volume4', 'cluster=cluster1', 'flag=thick,scsi'],
		[TestAction.create_volume, 'volume5', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.attach_volume, 'vm2', 'volume5'],
		[TestAction.create_volume_backup, 'volume5', 'volume5-backup5'],
		[TestAction.delete_volume_backup, 'volume5-backup5'],
		[TestAction.destroy_vm, 'vm2'],
		[TestAction.expunge_vm, 'vm2'],
		[TestAction.delete_volume, 'volume1'],
		[TestAction.expunge_volume, 'volume1'],
		[TestAction.create_mini_vm, 'vm4', 'cluster=cluster2'],
		[TestAction.create_vm_backup, 'vm4', 'vm4-backup6'],
		[TestAction.create_image_from_volume, 'vm1', 'vm1-image2'],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.use_vm_backup, 'vm3-backup3'],
])




'''
The final status:
Running:['vm1', 'vm4']
Stopped:['vm3']
Enadbled:['volume1-backup1', 'vm3-backup3', 'volume2-backup3', 'vm4-backup6', 'vm1-image2']
attached:['volume2']
Detached:['volume3', 'volume4', 'volume5']
Deleted:['volume2-backup2', 'volume5-backup5']
Expunged:['vm2', 'volume1', 'image1']
Ha:[]
Group:
	vm_backup2:['vm4-backup6']---vm4@
	vm_backup1:['vm3-backup3', 'volume2-backup3']---vm3@volume2
'''