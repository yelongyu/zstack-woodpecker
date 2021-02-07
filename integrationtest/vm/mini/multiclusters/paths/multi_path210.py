import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", checking_point=1, faild_point=100000, path_list=[
		[TestAction.create_mini_vm, 'vm1', 'cluster=cluster2'],
		[TestAction.destroy_vm, 'vm1'],
		[TestAction.recover_vm, 'vm1'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.create_vm_backup, 'vm1', 'vm1-backup1'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.create_mini_vm, 'vm2', 'network=random', 'cluster=cluster1'],
		[TestAction.resize_volume, 'vm1', 5*1024*1024],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.create_volume, 'volume1', 'size=random', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.create_volume, 'volume2', 'cluster=cluster2', 'flag=thick,scsi'],
		[TestAction.add_image, 'image1', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.create_volume, 'volume3', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.attach_volume, 'vm2', 'volume3'],
		[TestAction.start_vm, 'vm2'],
		[TestAction.create_volume_backup, 'volume3', 'volume3-backup2'],
		[TestAction.stop_vm, 'vm2'],
		[TestAction.delete_volume_backup, 'volume3-backup2'],
		[TestAction.delete_image, 'image1'],
		[TestAction.expunge_image, 'image1'],
		[TestAction.attach_volume, 'vm1', 'volume1'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.create_volume_backup, 'volume1', 'volume1-backup3'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.create_mini_vm, 'vm3', 'data_volume=true', 'cluster=cluster2'],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.create_image_from_volume, 'vm2', 'vm2-image2'],
		[TestAction.detach_volume, 'volume3'],
		[TestAction.delete_volume, 'volume3'],
		[TestAction.create_volume, 'volume5', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.attach_volume, 'vm2', 'volume5'],
		[TestAction.start_vm, 'vm2'],
		[TestAction.create_volume_backup, 'volume5', 'volume5-backup4'],
		[TestAction.stop_vm, 'vm2'],
		[TestAction.use_volume_backup, 'volume5-backup4'],
		[TestAction.create_mini_vm, 'vm4', 'cpu=random', 'cluster=cluster2'],
		[TestAction.delete_volume, 'volume2'],
		[TestAction.expunge_volume, 'volume2'],
		[TestAction.create_mini_vm, 'vm5', 'cluster=cluster1'],
		[TestAction.create_vm_backup, 'vm5', 'vm5-backup5'],
		[TestAction.create_image_from_volume, 'vm1', 'vm1-image3'],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.create_volume, 'volume6', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.attach_volume, 'vm5', 'volume6'],
		[TestAction.create_volume_backup, 'volume6', 'volume6-backup6'],
		[TestAction.stop_vm, 'vm5'],
		[TestAction.use_volume_backup, 'volume6-backup6'],
		[TestAction.start_vm, 'vm5'],
])




'''
The final status:
Running:['vm5']
Stopped:['vm1', 'vm3', 'vm2', 'vm4']
Enadbled:['vm1-backup1', 'volume1-backup3', 'volume5-backup4', 'vm5-backup5', 'volume6-backup6', 'vm2-image2', 'vm1-image3']
attached:['volume1', 'auto-volume3', 'volume5', 'volume6']
Detached:[]
Deleted:['volume3', 'volume3-backup2']
Expunged:['volume2', 'image1']
Ha:[]
Group:
	vm_backup2:['vm5-backup5']---vm5@
	vm_backup1:['vm1-backup1']---vm1@
'''