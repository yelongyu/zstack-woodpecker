import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", checking_point=1, faild_point=100000, path_list=[
		[TestAction.create_mini_vm, 'vm1', 'cluster=cluster2'],
		[TestAction.create_volume, 'volume1', 'flag=scsi'],
		[TestAction.attach_volume, 'vm1', 'volume1'],
		[TestAction.create_volume_backup, 'volume1', 'volume1-backup1'],
		[TestAction.detach_volume, 'volume1'],
		[TestAction.create_mini_vm, 'vm2', 'cluster=cluster1'],
		[TestAction.start_vm, 'vm2'],
		[TestAction.stop_vm, 'vm2'],
		[TestAction.create_volume, 'volume2', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.resize_data_volume, 'volume2', 5*1024*1024],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.create_volume, 'volume3', 'size=random', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.create_volume, 'volume4', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.delete_volume, 'volume4'],
		[TestAction.add_image, 'image1', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.attach_volume, 'vm2', 'volume1'],
		[TestAction.use_volume_backup, 'volume1-backup1'],
		[TestAction.detach_volume, 'volume1'],
		[TestAction.delete_image, 'image1'],
		[TestAction.recover_image, 'image1'],
		[TestAction.delete_image, 'image1'],
		[TestAction.expunge_image, 'image1'],
		[TestAction.attach_volume, 'vm1', 'volume1'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.create_volume_backup, 'volume1', 'volume1-backup2'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.detach_volume, 'volume1'],
		[TestAction.add_image, 'image2', 'root', os.environ.get('isoForVmUrl')],
		[TestAction.create_vm_by_image, 'image2', 'iso', 'vm3', 'cluster=cluster2'],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.create_image_from_volume, 'vm2', 'vm2-image3'],
		[TestAction.create_volume, 'volume5', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.attach_volume, 'vm1', 'volume5'],
		[TestAction.create_volume, 'volume6', 'cluster=cluster2', 'flag=thick,scsi'],
		[TestAction.delete_volume_backup, 'volume1-backup1'],
		[TestAction.start_vm, 'vm2'],
		[TestAction.delete_volume, 'volume5'],
		[TestAction.expunge_volume, 'volume5'],
		[TestAction.destroy_vm, 'vm1'],
		[TestAction.recover_vm, 'vm1'],
		[TestAction.start_vm, 'vm3'],
		[TestAction.create_vm_backup, 'vm3', 'vm3-backup3'],
		[TestAction.stop_vm, 'vm3'],
		[TestAction.resize_data_volume, 'volume3', 5*1024*1024],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.use_vm_backup, 'vm3-backup3'],
])




'''
The final status:
Running:['vm2']
Stopped:['vm1', 'vm3']
Enadbled:['volume1-backup2', 'vm3-backup3', 'image2', 'vm2-image3']
attached:[]
Detached:['volume2', 'volume3', 'volume1', 'volume6']
Deleted:['volume4', 'volume1-backup1']
Expunged:['volume5', 'image1']
Ha:[]
Group:
	vm_backup1:['vm3-backup3']---vm3@
'''