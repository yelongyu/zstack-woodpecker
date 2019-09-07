import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", checking_point=1, faild_point=100000, path_list=[
		[TestAction.create_mini_vm, 'vm1', 'cluster=cluster1'],
		[TestAction.destroy_vm, 'vm1'],
		[TestAction.create_mini_vm, 'vm2', 'cluster=cluster1'],
		[TestAction.create_vm_backup, 'vm2', 'vm2-backup1'],
		[TestAction.create_mini_vm, 'vm3', 'network=random', 'cluster=cluster1'],
		[TestAction.migrate_vm, 'vm3'],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.create_volume, 'volume1', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.attach_volume, 'vm2', 'volume1'],
		[TestAction.create_volume, 'volume2', 'cluster=cluster2', 'flag=thick,scsi'],
		[TestAction.add_image, 'image1', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.attach_volume, 'vm2', 'volume2'],
		[TestAction.create_volume_backup, 'volume2', 'volume2-backup2'],
		[TestAction.stop_vm, 'vm2'],
		[TestAction.use_volume_backup, 'volume2-backup2'],
		[TestAction.start_vm, 'vm2'],
		[TestAction.detach_volume, 'volume2'],
		[TestAction.delete_image, 'image1'],
		[TestAction.expunge_image, 'image1'],
		[TestAction.attach_volume, 'vm2', 'volume2'],
		[TestAction.create_volume_backup, 'volume2', 'volume2-backup3'],
		[TestAction.detach_volume, 'volume2'],
		[TestAction.create_mini_vm, 'vm4', 'cluster=cluster2'],
		[TestAction.change_vm_ha, 'vm4'],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.create_image_from_volume, 'vm2', 'vm2-image2'],
		[TestAction.attach_volume, 'vm4', 'volume2'],
		[TestAction.detach_volume, 'volume2'],
		[TestAction.create_volume, 'volume3', 'cluster=cluster2', 'flag=thick,scsi'],
		[TestAction.use_vm_backup, 'vm2-backup1'],
		[TestAction.create_mini_vm, 'vm5', 'memory=random', 'cluster=cluster1'],
		[TestAction.delete_volume, 'volume2'],
		[TestAction.expunge_volume, 'volume2'],
		[TestAction.create_mini_vm, 'vm6', 'cluster=cluster2'],
		[TestAction.attach_volume, 'vm2', 'volume3'],
		[TestAction.start_vm, 'vm2'],
		[TestAction.create_volume_backup, 'volume3', 'volume3-backup4'],
		[TestAction.stop_vm, 'vm2'],
		[TestAction.detach_volume, 'volume3'],
		[TestAction.create_image_from_volume, 'vm5', 'vm5-image3'],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.delete_volume_backup, 'volume3-backup4'],
])




'''
The final status:
Running:['vm4', 'vm5']
Stopped:['vm3', 'vm2', 'vm6']
Enadbled:['vm2-backup1', 'volume2-backup2', 'volume2-backup3', 'vm2-image2', 'vm5-image3']
attached:['volume1']
Detached:['volume3']
Deleted:['vm1', 'volume3-backup4']
Expunged:['volume2', 'image1']
Ha:['vm4']
Group:
	vm_backup1:['vm2-backup1']---vm2@
'''