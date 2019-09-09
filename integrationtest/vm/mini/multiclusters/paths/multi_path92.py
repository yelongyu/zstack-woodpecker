import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", checking_point=1, faild_point=100000, path_list=[
		[TestAction.create_mini_vm, 'vm1', 'cluster=cluster1'],
		[TestAction.destroy_vm, 'vm1'],
		[TestAction.recover_vm, 'vm1'],
		[TestAction.create_mini_vm, 'vm2', 'cluster=cluster2'],
		[TestAction.create_volume, 'volume1', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.attach_volume, 'vm2', 'volume1'],
		[TestAction.create_volume_backup, 'volume1', 'volume1-backup1'],
		[TestAction.create_mini_vm, 'vm3', 'cpu=random', 'cluster=cluster1'],
		[TestAction.create_image_from_volume, 'vm2', 'vm2-image1'],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.create_volume, 'volume2', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.attach_volume, 'vm2', 'volume2'],
		[TestAction.create_volume, 'volume3', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.delete_volume, 'volume3'],
		[TestAction.recover_volume, 'volume3'],
		[TestAction.add_image, 'image2', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.create_volume, 'volume4', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.attach_volume, 'vm2', 'volume4'],
		[TestAction.create_volume_backup, 'volume4', 'volume4-backup2'],
		[TestAction.stop_vm, 'vm2'],
		[TestAction.use_volume_backup, 'volume4-backup2'],
		[TestAction.start_vm, 'vm2'],
		[TestAction.delete_image, 'image2'],
		[TestAction.delete_image, 'vm2-image1'],
		[TestAction.expunge_image, 'vm2-image1'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.create_vm_backup, 'vm1', 'vm1-backup3'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.create_mini_vm, 'vm4', 'cluster=cluster2'],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.start_vm, 'vm2'],
		[TestAction.migrate_vm, 'vm2'],
		[TestAction.attach_volume, 'vm1', 'volume3'],
		[TestAction.delete_volume, 'volume3'],
		[TestAction.recover_volume, 'volume3'],
		[TestAction.delete_vm_backup, 'vm1-backup3'],
		[TestAction.create_mini_vm, 'vm5', 'cpu=random', 'cluster=cluster2'],
		[TestAction.delete_volume, 'volume3'],
		[TestAction.expunge_volume, 'volume3'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.reboot_vm, 'vm1'],
		[TestAction.create_volume, 'volume5', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.attach_volume, 'vm2', 'volume5'],
		[TestAction.create_volume_backup, 'volume5', 'volume5-backup4'],
		[TestAction.migrate_vm, 'vm2'],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.start_vm, 'vm5'],
		[TestAction.create_vm_backup, 'vm5', 'vm5-backup5'],
		[TestAction.stop_vm, 'vm5'],
		[TestAction.use_vm_backup, 'vm5-backup5'],
])




'''
The final status:
Running:['vm1']
Stopped:['vm4', 'vm3', 'vm2', 'vm5']
Enadbled:['volume1-backup1', 'volume4-backup2', 'volume5-backup4', 'vm5-backup5']
attached:['volume1', 'volume2', 'volume4', 'volume5']
Detached:[]
Deleted:['vm1-backup3', 'image2']
Expunged:['volume3', 'vm2-image1']
Ha:[]
Group:
	vm_backup1:['vm5-backup5']---vm5@
'''