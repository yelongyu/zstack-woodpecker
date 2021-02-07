import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", checking_point=1, faild_point=100000, path_list=[
		[TestAction.create_mini_vm, 'vm1', 'cluster=cluster2'],
		[TestAction.create_mini_vm, 'vm2', 'cluster=cluster1'],
		[TestAction.create_volume, 'volume1', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.attach_volume, 'vm2', 'volume1'],
		[TestAction.create_volume_backup, 'volume1', 'volume1-backup1'],
		[TestAction.create_mini_vm, 'vm3', 'cluster=cluster1', 'flag=thick'],
		[TestAction.resize_volume, 'vm2', 5*1024*1024],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.create_volume, 'volume2', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.attach_volume, 'vm2', 'volume2'],
		[TestAction.delete_volume, 'volume2'],
		[TestAction.add_image, 'image1', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.create_volume, 'volume3', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.attach_volume, 'vm1', 'volume3'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.create_volume_backup, 'volume3', 'volume3-backup2'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.use_volume_backup, 'volume3-backup2'],
		[TestAction.delete_image, 'image1'],
		[TestAction.expunge_image, 'image1'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.create_vm_backup, 'vm1', 'vm1-backup3'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.destroy_vm, 'vm1'],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.create_image_from_volume, 'vm3', 'vm3-image2'],
		[TestAction.create_mini_vm, 'vm4', 'cluster=cluster2'],
		[TestAction.attach_volume, 'vm4', 'volume3'],
		[TestAction.detach_volume, 'volume3'],
		[TestAction.recover_volume, 'volume2'],
		[TestAction.create_vm_backup, 'vm4', 'vm4-backup5'],
		[TestAction.delete_vm_backup, 'vm4-backup5'],
		[TestAction.create_mini_vm, 'vm5', 'cpu=random', 'cluster=cluster2'],
		[TestAction.delete_volume, 'volume1'],
		[TestAction.expunge_volume, 'volume1'],
		[TestAction.destroy_vm, 'vm3'],
		[TestAction.recover_vm, 'vm3'],
		[TestAction.attach_volume, 'vm4', 'volume3'],
		[TestAction.create_volume_backup, 'volume3', 'volume3-backup6'],
		[TestAction.create_image_from_volume, 'vm2', 'vm2-image3'],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.create_vm_backup, 'vm5', 'vm5-backup7'],
		[TestAction.delete_vm_backup, 'vm5-backup7'],
])




'''
The final status:
Running:['vm4', 'vm5']
Stopped:['vm3', 'vm2']
Enadbled:['volume1-backup1', 'volume3-backup2', 'vm1-backup3', 'volume3-backup3', 'volume3-backup6', 'vm3-image2', 'vm2-image3']
attached:['volume3']
Detached:['volume2']
Deleted:['vm1', 'vm4-backup5', 'vm5-backup7']
Expunged:['volume1', 'image1']
Ha:[]
Group:
	vm_backup1:['vm1-backup3', 'volume3-backup3']---vm1@volume3
'''