import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", checking_point=1, faild_point=100000, path_list=[
		[TestAction.add_image, 'image1', 'root', os.environ.get('isoForVmUrl')],
		[TestAction.create_vm_by_image, 'image1', 'iso', 'vm1', 'cluster=cluster2'],
		[TestAction.create_mini_vm, 'vm2', 'cluster=cluster1'],
		[TestAction.create_vm_backup, 'vm2', 'vm2-backup1'],
		[TestAction.destroy_vm, 'vm2'],
		[TestAction.expunge_vm, 'vm2'],
		[TestAction.create_volume, 'volume1', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.resize_data_volume, 'volume1', 5*1024*1024],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.attach_volume, 'vm1', 'volume1'],
		[TestAction.create_volume, 'volume2', 'cluster=cluster2', 'flag=thick,scsi'],
		[TestAction.add_image, 'image2', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.attach_volume, 'vm1', 'volume2'],
		[TestAction.create_volume_backup, 'volume2', 'volume2-backup2'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.use_volume_backup, 'volume2-backup2'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.delete_image, 'image2'],
		[TestAction.expunge_image, 'image2'],
		[TestAction.create_vm_backup, 'vm1', 'vm1-backup3'],
		[TestAction.reboot_vm, 'vm1'],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.create_volume, 'volume3', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.resize_data_volume, 'volume3', 5*1024*1024],
		[TestAction.create_volume, 'volume4', 'size=random', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.delete_volume, 'volume1'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.use_volume_backup, 'volume2-backup3'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.create_mini_vm, 'vm3', 'cpu=random', 'cluster=cluster1'],
		[TestAction.expunge_volume, 'volume1'],
		[TestAction.create_mini_vm, 'vm4', 'data_volume=true', 'cluster=cluster1'],
		[TestAction.attach_volume, 'vm3', 'volume4'],
		[TestAction.create_volume_backup, 'volume4', 'volume4-backup6'],
		[TestAction.create_image_from_volume, 'vm4', 'vm4-image3'],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.attach_volume, 'vm4', 'volume3'],
		[TestAction.create_volume_backup, 'volume3', 'volume3-backup7'],
		[TestAction.delete_volume_backup, 'volume3-backup7'],
])




'''
The final status:
Running:['vm3', 'vm4']
Stopped:['vm1']
Enadbled:['vm2-backup1', 'volume2-backup2', 'vm1-backup3', 'volume1-backup3', 'volume2-backup3', 'volume4-backup6', 'image1', 'vm4-image3']
attached:['volume2', 'auto-volume4', 'volume4', 'volume3']
Detached:[]
Deleted:['volume3-backup7']
Expunged:['vm2', 'volume1', 'image2']
Ha:[]
Group:
	vm_backup2:['vm1-backup3', 'volume1-backup3', 'volume2-backup3']---vm1@volume1_volume2
	vm_backup1:['vm2-backup1']---vm2@
'''