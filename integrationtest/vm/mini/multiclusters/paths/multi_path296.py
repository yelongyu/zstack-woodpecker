import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", checking_point=1, faild_point=100000, path_list=[
		[TestAction.create_mini_vm, 'vm1', 'cluster=cluster1'],
		[TestAction.destroy_vm, 'vm1'],
		[TestAction.recover_vm, 'vm1'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.create_vm_backup, 'vm1', 'vm1-backup1'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.destroy_vm, 'vm1'],
		[TestAction.expunge_vm, 'vm1'],
		[TestAction.create_volume, 'volume1', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.resize_data_volume, 'volume1', 5*1024*1024],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.create_mini_vm, 'vm2', 'cluster=cluster2'],
		[TestAction.create_volume, 'volume2', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.attach_volume, 'vm2', 'volume2'],
		[TestAction.create_volume, 'volume3', 'cluster=cluster1', 'flag=thick,scsi'],
		[TestAction.add_image, 'image1', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.create_vm_backup, 'vm2', 'vm2-backup2'],
		[TestAction.stop_vm, 'vm2'],
		[TestAction.use_vm_backup, 'vm2-backup2'],
		[TestAction.start_vm, 'vm2'],
		[TestAction.delete_image, 'image1'],
		[TestAction.expunge_image, 'image1'],
		[TestAction.create_vm_backup, 'vm2', 'vm2-backup4'],
		[TestAction.destroy_vm, 'vm2'],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.create_mini_vm, 'vm3', 'cluster=cluster1'],
		[TestAction.create_image_from_volume, 'vm3', 'vm3-image2'],
		[TestAction.create_mini_vm, 'vm4', 'cluster=cluster2'],
		[TestAction.attach_volume, 'vm4', 'volume2'],
		[TestAction.detach_volume, 'volume2'],
		[TestAction.create_volume, 'volume4', 'cluster=cluster2', 'flag=thick,scsi'],
		[TestAction.attach_volume, 'vm4', 'volume4'],
		[TestAction.create_volume_backup, 'volume4', 'volume4-backup6'],
		[TestAction.stop_vm, 'vm4'],
		[TestAction.use_volume_backup, 'volume4-backup6'],
		[TestAction.start_vm, 'vm4'],
		[TestAction.destroy_vm, 'vm4'],
		[TestAction.expunge_vm, 'vm4'],
		[TestAction.delete_volume, 'volume2'],
		[TestAction.expunge_volume, 'volume2'],
		[TestAction.destroy_vm, 'vm3'],
		[TestAction.create_mini_vm, 'vm5', 'cluster=cluster1'],
		[TestAction.attach_volume, 'vm5', 'volume1'],
		[TestAction.create_volume_backup, 'volume1', 'volume1-backup7'],
		[TestAction.create_image_from_volume, 'vm5', 'vm5-image3'],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.create_mini_vm, 'vm6', 'cluster=cluster2'],
		[TestAction.attach_volume, 'vm6', 'volume4'],
		[TestAction.create_volume_backup, 'volume4', 'volume4-backup8'],
		[TestAction.delete_volume_backup, 'volume4-backup8'],
])




'''
The final status:
Running:['vm5', 'vm6']
Stopped:[]
Enadbled:['vm1-backup1', 'vm2-backup2', 'volume2-backup2', 'vm2-backup4', 'volume2-backup4', 'volume4-backup6', 'volume1-backup7', 'vm3-image2', 'vm5-image3']
attached:['volume1', 'volume4']
Detached:['volume3']
Deleted:['vm2', 'vm3', 'volume4-backup8']
Expunged:['vm1', 'vm4', 'volume2', 'image1']
Ha:[]
Group:
	vm_backup2:['vm2-backup2', 'volume2-backup2']---vm2@volume2
	vm_backup3:['vm2-backup4', 'volume2-backup4']---vm2@volume2
	vm_backup1:['vm1-backup1']---vm1@
'''