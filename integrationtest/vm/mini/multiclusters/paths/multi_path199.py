import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", checking_point=1, faild_point=100000, path_list=[
		[TestAction.create_mini_vm, 'vm1', 'cluster=cluster1'],
		[TestAction.destroy_vm, 'vm1'],
		[TestAction.create_mini_vm, 'vm2', 'cluster=cluster2'],
		[TestAction.create_vm_backup, 'vm2', 'vm2-backup1'],
		[TestAction.create_mini_vm, 'vm3', 'cluster=cluster2', 'flag=thin'],
		[TestAction.create_image_from_volume, 'vm3', 'vm3-image1'],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.create_volume, 'volume1', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.create_mini_vm, 'vm4', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.attach_volume, 'vm4', 'volume1'],
		[TestAction.detach_volume, 'volume1'],
		[TestAction.delete_volume, 'volume1'],
		[TestAction.recover_volume, 'volume1'],
		[TestAction.add_image, 'image2', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.stop_vm, 'vm2'],
		[TestAction.use_vm_backup, 'vm2-backup1'],
		[TestAction.start_vm, 'vm2'],
		[TestAction.delete_image, 'vm3-image1'],
		[TestAction.expunge_image, 'vm3-image1'],
		[TestAction.create_vm_backup, 'vm4', 'vm4-backup2'],
		[TestAction.create_mini_vm, 'vm5', 'cluster=cluster1'],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.create_volume, 'volume2', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.resize_data_volume, 'volume2', 5*1024*1024],
		[TestAction.attach_volume, 'vm2', 'volume2'],
		[TestAction.delete_volume, 'volume2'],
		[TestAction.recover_volume, 'volume2'],
		[TestAction.attach_volume, 'vm4', 'volume2'],
		[TestAction.create_volume_backup, 'volume2', 'volume2-backup3'],
		[TestAction.stop_vm, 'vm4'],
		[TestAction.use_volume_backup, 'volume2-backup3'],
		[TestAction.start_vm, 'vm4'],
		[TestAction.detach_volume, 'volume2'],
		[TestAction.create_mini_vm, 'vm6', 'cluster=cluster2', 'flag=thick'],
		[TestAction.delete_volume, 'volume1'],
		[TestAction.expunge_volume, 'volume1'],
		[TestAction.change_vm_ha, 'vm4'],
		[TestAction.start_vm, 'vm2'],
		[TestAction.create_vm_backup, 'vm2', 'vm2-backup4'],
		[TestAction.stop_vm, 'vm2'],
		[TestAction.resize_volume, 'vm4', 5*1024*1024],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.use_vm_backup, 'vm2-backup1'],
])




'''
The final status:
Running:['vm4', 'vm6']
Stopped:['vm3', 'vm5', 'vm2']
Enadbled:['vm2-backup1', 'vm4-backup2', 'volume2-backup3', 'vm2-backup4', 'image2']
attached:[]
Detached:['volume2']
Deleted:['vm1']
Expunged:['volume1', 'vm3-image1']
Ha:['vm4']
Group:
	vm_backup2:['vm4-backup2']---vm4@
	vm_backup3:['vm2-backup4']---vm2@
	vm_backup1:['vm2-backup1']---vm2@
'''