import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", checking_point=1, faild_point=100000, path_list=[
		[TestAction.create_mini_vm, 'vm1', 'cluster=cluster1'],
		[TestAction.reboot_vm, 'vm1'],
		[TestAction.create_vm_backup, 'vm1', 'vm1-backup1'],
		[TestAction.create_mini_vm, 'vm2', 'cluster=cluster1', 'flag=thin'],
		[TestAction.create_mini_vm, 'vm3', 'cluster=cluster2'],
		[TestAction.migrate_vm, 'vm3'],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.create_volume, 'volume1', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.attach_volume, 'vm3', 'volume1'],
		[TestAction.create_volume, 'volume2', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.delete_volume, 'volume2'],
		[TestAction.recover_volume, 'volume2'],
		[TestAction.add_image, 'image1', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.create_volume, 'volume3', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.attach_volume, 'vm3', 'volume3'],
		[TestAction.start_vm, 'vm3'],
		[TestAction.create_volume_backup, 'volume3', 'volume3-backup2'],
		[TestAction.stop_vm, 'vm3'],
		[TestAction.use_volume_backup, 'volume3-backup2'],
		[TestAction.delete_image, 'image1'],
		[TestAction.recover_image, 'image1'],
		[TestAction.delete_image, 'image1'],
		[TestAction.expunge_image, 'image1'],
		[TestAction.create_volume, 'volume4', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.attach_volume, 'vm3', 'volume4'],
		[TestAction.start_vm, 'vm3'],
		[TestAction.create_volume_backup, 'volume4', 'volume4-backup3'],
		[TestAction.stop_vm, 'vm3'],
		[TestAction.change_vm_ha, 'vm2'],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.create_image_from_volume, 'vm3', 'vm3-image2'],
		[TestAction.create_volume, 'volume5', 'size=random', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.delete_volume, 'volume2'],
		[TestAction.create_volume, 'volume6', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.attach_volume, 'vm3', 'volume6'],
		[TestAction.start_vm, 'vm3'],
		[TestAction.create_volume_backup, 'volume6', 'volume6-backup4'],
		[TestAction.stop_vm, 'vm3'],
		[TestAction.use_volume_backup, 'volume6-backup4'],
		[TestAction.create_mini_vm, 'vm4', 'cluster=cluster2', 'flag=thick'],
		[TestAction.expunge_volume, 'volume2'],
		[TestAction.create_mini_vm, 'vm5', 'cluster=cluster2'],
		[TestAction.create_vm_backup, 'vm2', 'vm2-backup5'],
		[TestAction.resize_volume, 'vm5', 5*1024*1024],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.delete_volume_backup, 'volume6-backup4'],
])




'''
The final status:
Running:['vm2', 'vm4', 'vm5']
Stopped:['vm3', 'vm1']
Enadbled:['vm1-backup1', 'volume3-backup2', 'volume4-backup3', 'vm2-backup5', 'vm3-image2']
attached:['volume1', 'volume3', 'volume4', 'volume6']
Detached:['volume5']
Deleted:['volume6-backup4']
Expunged:['volume2', 'image1']
Ha:['vm2']
Group:
	vm_backup2:['vm2-backup5']---vm2@
	vm_backup1:['vm1-backup1']---vm1@
'''