import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", path_list=[
		[TestAction.create_mini_vm, 'vm1', ],
		[TestAction.reboot_vm, 'vm1'],
		[TestAction.create_vm_backup, 'vm1', 'vm1-backup1'],
		[TestAction.create_mini_vm, 'vm2', 'flag=thick'],
		[TestAction.create_image_from_volume, 'vm1', 'vm1-image1'],
		[TestAction.create_volume, 'volume1', 'size=random', 'flag=scsi'],
		[TestAction.create_mini_vm, 'vm3', 'network=random'],
		[TestAction.delete_volume, 'volume1'],
		[TestAction.add_image, 'image2', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.recover_volume, 'volume1'],
		[TestAction.attach_volume, 'vm1', 'volume1'],
		[TestAction.create_volume_backup, 'volume1', 'volume1-backup2'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.use_volume_backup, 'volume1-backup2'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.detach_volume, 'volume1'],
		[TestAction.delete_image, 'image2'],
		[TestAction.recover_image, 'image2'],
		[TestAction.delete_image, 'vm1-image1'],
		[TestAction.expunge_image, 'vm1-image1'],
		[TestAction.create_vm_backup, 'vm2', 'vm2-backup3'],
		[TestAction.change_vm_ha, 'vm1'],
		[TestAction.resize_volume, 'vm2', 5*1024*1024],
		[TestAction.create_volume, 'volume2', 'flag=scsi'],
		[TestAction.attach_volume, 'vm3', 'volume1'],
		[TestAction.create_volume, 'volume3', 'flag=thick,scsi'],
		[TestAction.create_mini_vm, 'vm4', 'flag=thin'],
		[TestAction.add_image, 'image3', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.delete_volume, 'volume2'],
		[TestAction.expunge_volume, 'volume2'],
		[TestAction.create_mini_vm, 'vm5', ],
		[TestAction.create_volume_backup, 'volume1', 'volume1-backup4'],
		[TestAction.resize_data_volume, 'volume3', 5*1024*1024],
		[TestAction.delete_image, 'image2'],
		[TestAction.stop_vm, 'vm2'],
		[TestAction.use_vm_backup, 'vm2-backup3'],
		[TestAction.start_vm, 'vm2'],
		[TestAction.add_image, 'image4', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.create_volume, 'volume4', 'flag=scsi'],
		[TestAction.attach_volume, 'vm5', 'volume3'],
])



'''
The final status:
Running:['vm3', 'vm1', 'vm4', 'vm5', 'vm2']
Stopped:[]
Enadbled:['vm1-backup1', 'volume1-backup2', 'vm2-backup3', 'volume1-backup4', 'image3', 'image4']
attached:['volume1', 'volume3']
Detached:['volume4']
Deleted:['image2']
Expunged:['volume2', 'vm1-image1']
Ha:['vm1']
Group:
	vm_backup2:['vm2-backup3']---vm2_
	vm_backup1:['vm1-backup1']---vm1_
'''
