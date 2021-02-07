import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", checking_point=1, faild_point=100000, path_list=[
		[TestAction.create_mini_vm, 'vm1', 'cluster=cluster2'],
		[TestAction.destroy_vm, 'vm1'],
		[TestAction.recover_vm, 'vm1'],
		[TestAction.create_mini_vm, 'vm2', 'cluster=cluster1'],
		[TestAction.create_vm_backup, 'vm2', 'vm2-backup1'],
		[TestAction.create_mini_vm, 'vm3', 'cluster=cluster1'],
		[TestAction.stop_vm, 'vm3'],
		[TestAction.start_vm, 'vm3'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.migrate_vm, 'vm1'],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.create_volume, 'volume1', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.attach_volume, 'vm1', 'volume1'],
		[TestAction.create_volume, 'volume2', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.delete_volume, 'volume2'],
		[TestAction.add_image, 'image1', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.create_volume, 'volume3', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.attach_volume, 'vm2', 'volume3'],
		[TestAction.create_volume_backup, 'volume3', 'volume3-backup2'],
		[TestAction.delete_volume_backup, 'volume3-backup2'],
		[TestAction.delete_image, 'image1'],
		[TestAction.recover_image, 'image1'],
		[TestAction.delete_image, 'image1'],
		[TestAction.expunge_image, 'image1'],
		[TestAction.create_volume, 'volume4', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.attach_volume, 'vm1', 'volume4'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.create_volume_backup, 'volume4', 'volume4-backup3'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.change_vm_ha, 'vm1'],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.create_image_from_volume, 'vm3', 'vm3-image2'],
		[TestAction.detach_volume, 'volume4'],
		[TestAction.create_volume, 'volume5', 'cluster=cluster2', 'flag=thin,scsi'],
		[TestAction.use_volume_backup, 'volume4-backup3'],
		[TestAction.start_vm, 'vm2'],
		[TestAction.delete_volume, 'volume3'],
		[TestAction.expunge_volume, 'volume3'],
		[TestAction.destroy_vm, 'vm3'],
		[TestAction.attach_volume, 'vm1', 'volume4'],
		[TestAction.create_volume_backup, 'volume4', 'volume4-backup4'],
		[TestAction.migrate_vm, 'vm1'],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.stop_vm, 'vm2'],
		[TestAction.use_vm_backup, 'vm2-backup1'],
		[TestAction.start_vm, 'vm2'],
])




'''
The final status:
Running:['vm1', 'vm2']
Stopped:[]
Enadbled:['vm2-backup1', 'volume4-backup3', 'volume4-backup4', 'vm3-image2']
attached:['volume1', 'volume4']
Detached:['volume5']
Deleted:['vm3', 'volume2', 'volume3-backup2']
Expunged:['volume3', 'image1']
Ha:['vm1']
Group:
	vm_backup1:['vm2-backup1']---vm2@
'''