import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", checking_point=1, faild_point=100000, path_list=[
		[TestAction.create_mini_vm, 'vm1', 'cluster=cluster2'],
		[TestAction.destroy_vm, 'vm1'],
		[TestAction.create_mini_vm, 'vm2', 'cluster=cluster1'],
		[TestAction.create_vm_backup, 'vm2', 'vm2-backup1'],
		[TestAction.destroy_vm, 'vm2'],
		[TestAction.expunge_vm, 'vm2'],
		[TestAction.create_mini_vm, 'vm3', 'cluster=cluster1'],
		[TestAction.resize_volume, 'vm3', 5*1024*1024],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.create_volume, 'volume1', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.attach_volume, 'vm3', 'volume1'],
		[TestAction.detach_volume, 'volume1'],
		[TestAction.create_volume, 'volume2', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.delete_volume, 'volume2'],
		[TestAction.add_image, 'image1', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.create_vm_backup, 'vm3', 'vm3-backup2'],
		[TestAction.stop_vm, 'vm3'],
		[TestAction.use_vm_backup, 'vm3-backup2'],
		[TestAction.start_vm, 'vm3'],
		[TestAction.delete_image, 'image1'],
		[TestAction.expunge_image, 'image1'],
		[TestAction.attach_volume, 'vm3', 'volume1'],
		[TestAction.create_volume_backup, 'volume1', 'volume1-backup3'],
		[TestAction.detach_volume, 'volume1'],
		[TestAction.add_image, 'image2', 'root', os.environ.get('isoForVmUrl')],
		[TestAction.create_vm_by_image, 'image2', 'iso', 'vm4', 'cluster=cluster1'],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.create_image_from_volume, 'vm3', 'vm3-image3'],
		[TestAction.attach_volume, 'vm3', 'volume1'],
		[TestAction.create_volume, 'volume3', 'cluster=cluster1', 'flag=thick,scsi'],
		[TestAction.stop_vm, 'vm3'],
		[TestAction.use_volume_backup, 'volume1-backup3'],
		[TestAction.start_vm, 'vm3'],
		[TestAction.create_mini_vm, 'vm5', 'network=random', 'cluster=cluster2'],
		[TestAction.expunge_volume, 'volume2'],
		[TestAction.change_vm_ha, 'vm5'],
		[TestAction.create_volume_backup, 'volume1', 'volume1-backup4'],
		[TestAction.resize_volume, 'vm5', 5*1024*1024],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.delete_vm_backup, 'vm3-backup2'],
])




'''
The final status:
Running:['vm5']
Stopped:['vm4', 'vm3']
Enadbled:['vm2-backup1', 'volume1-backup3', 'volume1-backup4', 'image2', 'vm3-image3']
attached:['volume1']
Detached:['volume3']
Deleted:['vm1', 'vm3-backup2']
Expunged:['vm2', 'volume2', 'image1']
Ha:['vm5']
Group:
	vm_backup1:['vm2-backup1']---vm2@
'''