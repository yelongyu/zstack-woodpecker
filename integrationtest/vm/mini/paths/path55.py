import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", path_list=[
		[TestAction.create_mini_vm, 'vm1', ],
		[TestAction.reboot_vm, 'vm1'],
		[TestAction.create_volume, 'volume1', 'flag=scsi'],
		[TestAction.attach_volume, 'vm1', 'volume1'],
		[TestAction.create_volume_backup, 'volume1', 'volume1-backup1'],
		[TestAction.detach_volume, 'volume1'],
		[TestAction.create_mini_vm, 'vm2', 'flag=thick'],
		[TestAction.create_image_from_volume, 'vm1', 'vm1-image1'],
		[TestAction.attach_volume, 'vm2', 'volume1'],
		[TestAction.create_mini_vm, 'vm3', 'network=random'],
		[TestAction.delete_volume, 'volume1'],
		[TestAction.recover_volume, 'volume1'],
		[TestAction.add_image, 'image2', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.delete_volume_backup, 'volume1-backup1'],
		[TestAction.delete_image, 'image2'],
		[TestAction.recover_image, 'image2'],
		[TestAction.delete_image, 'vm1-image1'],
		[TestAction.expunge_image, 'vm1-image1'],
		[TestAction.create_vm_backup, 'vm3', 'vm3-backup2'],
		[TestAction.reboot_vm, 'vm2'],
		[TestAction.create_image_from_volume, 'vm2', 'vm2-image3'],
		[TestAction.attach_volume, 'vm1', 'volume1'],
		[TestAction.create_volume, 'volume2', 'flag=thick,scsi'],
		[TestAction.create_mini_vm, 'vm4', 'memory=random'],
		[TestAction.add_image, 'image4', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.delete_volume, 'volume2'],
		[TestAction.expunge_volume, 'volume2'],
		[TestAction.destroy_vm, 'vm1'],
		[TestAction.create_vm_backup, 'vm3', 'vm3-backup3'],
		[TestAction.recover_vm, 'vm1'],
		[TestAction.create_image_from_volume, 'vm1', 'vm1-image5'],
		[TestAction.destroy_vm, 'vm1'],
		[TestAction.delete_image, 'vm1-image5'],
		[TestAction.stop_vm, 'vm3'],
		[TestAction.use_vm_backup, 'vm3-backup2'],
		[TestAction.start_vm, 'vm3'],
		[TestAction.add_image, 'image6', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.attach_volume, 'vm3', 'volume1'],
		[TestAction.detach_volume, 'volume1'],
])



'''
The final status:
Running:['vm2', 'vm4', 'vm3']
Stopped:[]
Enadbled:['vm3-backup2', 'vm3-backup3', 'image2', 'vm2-image3', 'image4', 'image6']
attached:[]
Detached:['volume1']
Deleted:['vm1', 'volume1-backup1', 'vm1-image5']
Expunged:['volume2', 'vm1-image1']
Ha:[]
Group:
	vm_backup2:['vm3-backup3']---vm3_
	vm_backup1:['vm3-backup2']---vm3_
'''
