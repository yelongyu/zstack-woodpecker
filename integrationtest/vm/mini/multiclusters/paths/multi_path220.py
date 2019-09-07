import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", checking_point=1, faild_point=100000, path_list=[
		[TestAction.create_mini_vm, 'vm1', 'cluster=cluster2'],
		[TestAction.reboot_vm, 'vm1'],
		[TestAction.create_mini_vm, 'vm2', 'cluster=cluster1'],
		[TestAction.create_vm_backup, 'vm2', 'vm2-backup1'],
		[TestAction.create_mini_vm, 'vm3', 'cluster=cluster1', 'flag=thin'],
		[TestAction.create_volume, 'volume1', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.resize_data_volume, 'volume1', 5*1024*1024],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.create_volume, 'volume2', 'size=random', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.delete_volume, 'volume1'],
		[TestAction.recover_volume, 'volume1'],
		[TestAction.add_image, 'image1', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.attach_volume, 'vm3', 'volume1'],
		[TestAction.create_volume_backup, 'volume1', 'volume1-backup2'],
		[TestAction.stop_vm, 'vm3'],
		[TestAction.use_volume_backup, 'volume1-backup2'],
		[TestAction.start_vm, 'vm3'],
		[TestAction.detach_volume, 'volume1'],
		[TestAction.delete_image, 'image1'],
		[TestAction.expunge_image, 'image1'],
		[TestAction.create_vm_backup, 'vm3', 'vm3-backup3'],
		[TestAction.add_image, 'image2', 'root', os.environ.get('isoForVmUrl')],
		[TestAction.create_vm_by_image, 'image2', 'iso', 'vm4', 'cluster=cluster2'],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.create_image_from_volume, 'vm4', 'vm4-image3'],
		[TestAction.create_volume, 'volume3', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.attach_volume, 'vm2', 'volume3'],
		[TestAction.delete_volume, 'volume1'],
		[TestAction.recover_volume, 'volume1'],
		[TestAction.delete_volume_backup, 'volume1-backup2'],
		[TestAction.start_vm, 'vm4'],
		[TestAction.stop_vm, 'vm4'],
		[TestAction.delete_volume, 'volume3'],
		[TestAction.expunge_volume, 'volume3'],
		[TestAction.create_vm_by_image, 'image2', 'iso', 'vm5', 'cluster=cluster1'],
		[TestAction.create_vm_backup, 'vm3', 'vm3-backup4'],
		[TestAction.create_volume, 'volume4', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.resize_data_volume, 'volume4', 5*1024*1024],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.delete_vm_backup, 'vm3-backup3'],
])




'''
The final status:
Running:[]
Stopped:['vm1', 'vm4', 'vm2', 'vm3', 'vm5']
Enadbled:['vm2-backup1', 'vm3-backup4', 'image2', 'vm4-image3']
attached:[]
Detached:['volume2', 'volume1', 'volume4']
Deleted:['volume1-backup2', 'vm3-backup3']
Expunged:['volume3', 'image1']
Ha:[]
Group:
	vm_backup3:['vm3-backup4']---vm3@
	vm_backup1:['vm2-backup1']---vm2@
'''