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
		[TestAction.create_mini_vm, 'vm2', 'cluster=cluster2'],
		[TestAction.destroy_vm, 'vm2'],
		[TestAction.expunge_vm, 'vm2'],
		[TestAction.create_mini_vm, 'vm3', 'cluster=cluster2'],
		[TestAction.resize_volume, 'vm1', 5*1024*1024],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.create_volume, 'volume2', 'size=random', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.delete_volume, 'volume2'],
		[TestAction.recover_volume, 'volume2'],
		[TestAction.add_image, 'image1', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.start_vm, 'vm3'],
		[TestAction.create_vm_backup, 'vm3', 'vm3-backup2'],
		[TestAction.delete_vm_backup, 'vm3-backup2'],
		[TestAction.stop_vm, 'vm3'],
		[TestAction.delete_image, 'image1'],
		[TestAction.expunge_image, 'image1'],
		[TestAction.create_vm_backup, 'vm1', 'vm1-backup3'],
		[TestAction.create_mini_vm, 'vm4', 'data_volume=true', 'cluster=cluster2'],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.resize_data_volume, 'volume2', 5*1024*1024],
		[TestAction.create_volume, 'volume4', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.attach_volume, 'vm4', 'volume4'],
		[TestAction.delete_volume, 'volume4'],
		[TestAction.delete_volume_backup, 'volume1-backup1'],
		[TestAction.create_mini_vm, 'vm5', 'cluster=cluster1'],
		[TestAction.start_vm, 'vm5'],
		[TestAction.delete_volume, 'volume2'],
		[TestAction.expunge_volume, 'volume2'],
		[TestAction.destroy_vm, 'vm3'],
		[TestAction.create_vm_backup, 'vm4', 'vm4-backup4'],
		[TestAction.create_image_from_volume, 'vm5', 'vm5-image2'],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.delete_vm_backup, 'vm1-backup3'],
])




'''
The final status:
Running:['vm1', 'vm5']
Stopped:['vm4']
Enadbled:['vm4-backup4', 'auto-volume4-backup4', 'vm5-image2']
attached:['auto-volume4']
Detached:['volume1']
Deleted:['vm3', 'volume4', 'vm3-backup2', 'volume1-backup1', 'vm1-backup3']
Expunged:['vm2', 'volume2', 'image1']
Ha:['vm1']
Group:
	vm_backup2:['vm4-backup4', 'auto-volume4-backup4']---vm4@auto-volume4
'''