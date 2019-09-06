import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", checking_point=1, faild_point=100000, path_list=[
		[TestAction.create_mini_vm, 'vm1', 'cluster=cluster1'],
		[TestAction.create_vm_backup, 'vm1', 'vm1-backup1'],
		[TestAction.create_mini_vm, 'vm2', 'memory=random', 'cluster=cluster1'],
		[TestAction.create_volume, 'volume1', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.resize_data_volume, 'volume1', 5*1024*1024],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.create_volume, 'volume2', 'size=random', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.create_volume, 'volume3', 'cluster=cluster1', 'flag=thick,scsi'],
		[TestAction.add_image, 'image1', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.delete_vm_backup, 'vm1-backup1'],
		[TestAction.delete_image, 'image1'],
		[TestAction.recover_image, 'image1'],
		[TestAction.delete_image, 'image1'],
		[TestAction.expunge_image, 'image1'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.create_vm_backup, 'vm1', 'vm1-backup2'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.create_mini_vm, 'vm3', 'cluster=cluster2'],
		[TestAction.change_vm_ha, 'vm3'],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.resize_volume, 'vm1', 5*1024*1024],
		[TestAction.attach_volume, 'vm1', 'volume3'],
		[TestAction.delete_volume, 'volume3'],
		[TestAction.recover_volume, 'volume3'],
		[TestAction.attach_volume, 'vm3', 'volume3'],
		[TestAction.create_volume_backup, 'volume3', 'volume3-backup3'],
		[TestAction.change_vm_ha, 'vm3'],
		[TestAction.stop_vm, 'vm3'],
		[TestAction.use_volume_backup, 'volume3-backup3'],
		[TestAction.start_vm, 'vm3'],
		[TestAction.change_vm_ha, 'vm3'],
		[TestAction.detach_volume, 'volume3'],
		[TestAction.create_mini_vm, 'vm4', 'cluster=cluster2'],
		[TestAction.start_vm, 'vm4'],
		[TestAction.delete_volume, 'volume2'],
		[TestAction.expunge_volume, 'volume2'],
		[TestAction.add_image, 'image2', 'root', os.environ.get('isoForVmUrl')],
		[TestAction.create_vm_by_image, 'image2', 'iso', 'vm5', 'cluster=cluster1'],
		[TestAction.attach_volume, 'vm5', 'volume3'],
		[TestAction.create_volume_backup, 'volume3', 'volume3-backup4'],
		[TestAction.detach_volume, 'volume3'],
		[TestAction.create_image_from_volume, 'vm3', 'vm3-image3'],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.use_vm_backup, 'vm1-backup2'],
])




'''
The final status:
Running:['vm3', 'vm4']
Stopped:['vm5', 'vm1', 'vm2']
Enadbled:['vm1-backup2', 'volume3-backup3', 'volume3-backup4', 'image2', 'vm3-image3']
attached:[]
Detached:['volume1', 'volume3']
Deleted:['vm1-backup1']
Expunged:['volume2', 'image1']
Ha:['vm3']
Group:
	vm_backup1:['vm1-backup2']---vm1@
'''