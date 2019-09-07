import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", checking_point=1, faild_point=100000, path_list=[
		[TestAction.add_image, 'image1', 'root', os.environ.get('isoForVmUrl')],
		[TestAction.create_vm_by_image, 'image1', 'iso', 'vm1', 'cluster=cluster2'],
		[TestAction.create_volume, 'volume1', 'flag=scsi'],
		[TestAction.attach_volume, 'vm1', 'volume1'],
		[TestAction.create_volume_backup, 'volume1', 'volume1-backup1'],
		[TestAction.detach_volume, 'volume1'],
		[TestAction.create_mini_vm, 'vm2', 'cluster=cluster2'],
		[TestAction.stop_vm, 'vm2'],
		[TestAction.start_vm, 'vm2'],
		[TestAction.create_mini_vm, 'vm3', 'cluster=cluster1'],
		[TestAction.create_image_from_volume, 'vm3', 'vm3-image2'],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.create_volume, 'volume2', 'size=random', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.create_volume, 'volume3', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.delete_volume, 'volume3'],
		[TestAction.recover_volume, 'volume3'],
		[TestAction.add_image, 'image3', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.attach_volume, 'vm2', 'volume1'],
		[TestAction.stop_vm, 'vm2'],
		[TestAction.use_volume_backup, 'volume1-backup1'],
		[TestAction.start_vm, 'vm2'],
		[TestAction.detach_volume, 'volume1'],
		[TestAction.delete_image, 'vm3-image2'],
		[TestAction.recover_image, 'vm3-image2'],
		[TestAction.delete_image, 'image1'],
		[TestAction.expunge_image, 'image1'],
		[TestAction.create_vm_backup, 'vm1', 'vm1-backup2'],
		[TestAction.create_mini_vm, 'vm4', 'cluster=cluster1'],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.create_image_from_volume, 'vm2', 'vm2-image4'],
		[TestAction.attach_volume, 'vm1', 'volume2'],
		[TestAction.detach_volume, 'volume2'],
		[TestAction.delete_volume, 'volume3'],
		[TestAction.attach_volume, 'vm4', 'volume1'],
		[TestAction.stop_vm, 'vm4'],
		[TestAction.use_volume_backup, 'volume1-backup1'],
		[TestAction.start_vm, 'vm4'],
		[TestAction.detach_volume, 'volume1'],
		[TestAction.start_vm, 'vm3'],
		[TestAction.stop_vm, 'vm3'],
		[TestAction.expunge_volume, 'volume3'],
		[TestAction.change_vm_ha, 'vm3'],
		[TestAction.attach_volume, 'vm4', 'volume2'],
		[TestAction.create_volume_backup, 'volume2', 'volume2-backup3'],
		[TestAction.detach_volume, 'volume2'],
		[TestAction.create_image_from_volume, 'vm3', 'vm3-image5'],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.delete_volume_backup, 'volume2-backup3'],
])




'''
The final status:
Running:['vm3']
Stopped:['vm1', 'vm2', 'vm4']
Enadbled:['volume1-backup1', 'vm1-backup2', 'image3', 'vm3-image2', 'vm2-image4', 'vm3-image5']
attached:[]
Detached:['volume1', 'volume2']
Deleted:['volume2-backup3']
Expunged:['volume3', 'image1']
Ha:['vm3']
Group:
	vm_backup1:['vm1-backup2']---vm1@
'''