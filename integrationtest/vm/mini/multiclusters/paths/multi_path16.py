import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", checking_point=1, faild_point=100000, path_list=[
		[TestAction.create_mini_vm, 'vm1', 'cluster=cluster1'],
		[TestAction.change_vm_ha, 'vm1'],
		[TestAction.create_volume, 'volume1', 'flag=scsi'],
		[TestAction.attach_volume, 'vm1', 'volume1'],
		[TestAction.create_volume_backup, 'volume1', 'volume1-backup1'],
		[TestAction.detach_volume, 'volume1'],
		[TestAction.create_mini_vm, 'vm2', 'network=random', 'cluster=cluster2'],
		[TestAction.create_image_from_volume, 'vm1', 'vm1-image1'],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.create_volume, 'volume2', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.attach_volume, 'vm2', 'volume2'],
		[TestAction.create_volume, 'volume3', 'cluster=cluster2', 'flag=thin,scsi'],
		[TestAction.add_image, 'image2', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.delete_volume_backup, 'volume1-backup1'],
		[TestAction.delete_image, 'image2'],
		[TestAction.delete_image, 'vm1-image1'],
		[TestAction.expunge_image, 'vm1-image1'],
		[TestAction.attach_volume, 'vm2', 'volume3'],
		[TestAction.create_volume_backup, 'volume3', 'volume3-backup2'],
		[TestAction.detach_volume, 'volume3'],
		[TestAction.create_mini_vm, 'vm3', 'cluster=cluster1'],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.create_image_from_volume, 'vm1', 'vm1-image3'],
		[TestAction.attach_volume, 'vm2', 'volume3'],
		[TestAction.delete_volume, 'volume2'],
		[TestAction.stop_vm, 'vm2'],
		[TestAction.use_volume_backup, 'volume3-backup2'],
		[TestAction.start_vm, 'vm2'],
		[TestAction.create_mini_vm, 'vm4', 'cluster=cluster1', 'flag=thin'],
		[TestAction.expunge_volume, 'volume2'],
		[TestAction.destroy_vm, 'vm4'],
		[TestAction.create_vm_backup, 'vm1', 'vm1-backup3'],
		[TestAction.migrate_vm, 'vm2'],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.create_vm_backup, 'vm2', 'vm2-backup4'],
		[TestAction.stop_vm, 'vm2'],
		[TestAction.use_vm_backup, 'vm2-backup4'],
		[TestAction.start_vm, 'vm2'],
])




'''
The final status:
Running:['vm1', 'vm3', 'vm2']
Stopped:[]
Enadbled:['volume3-backup2', 'vm1-backup3', 'vm2-backup4', 'volume3-backup4', 'vm1-image3']
attached:['volume3']
Detached:['volume1']
Deleted:['vm4', 'volume1-backup1', 'image2']
Expunged:['volume2', 'vm1-image1']
Ha:['vm1']
Group:
	vm_backup2:['vm2-backup4', 'volume3-backup4']---vm2@volume3
	vm_backup1:['vm1-backup3']---vm1@
'''