import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", path_list=[
		[TestAction.create_mini_vm, 'vm1', 'data_volume=true'],
		[TestAction.create_volume, 'volume1', 'flag=scsi'],
		[TestAction.attach_volume, 'vm1', 'volume1'],
		[TestAction.create_volume_backup, 'volume1', 'volume1-backup1'],
		[TestAction.detach_volume, 'volume1'],
		[TestAction.create_mini_vm, 'vm2', 'cpu=random'],
		[TestAction.migrate_vm, 'vm1'],
		[TestAction.create_volume, 'volume2', 'size=random', 'flag=scsi'],
		[TestAction.create_mini_vm, 'vm3', 'network=random'],
		[TestAction.create_volume, 'volume3', 'flag=thick,scsi'],
		[TestAction.add_image, 'image1', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.delete_volume_backup, 'volume1-backup1'],
		[TestAction.delete_image, 'image1'],
		[TestAction.expunge_image, 'image1'],
		[TestAction.create_vm_backup, 'vm3', 'vm3-backup2'],
		[TestAction.reboot_vm, 'vm3'],
		[TestAction.create_image_from_volume, 'vm2', 'vm2-image2'],
		[TestAction.create_volume, 'volume4', 'size=random', 'flag=scsi'],
		[TestAction.create_volume, 'volume5', 'flag=thick,scsi'],
		[TestAction.create_mini_vm, 'vm4', 'memory=random'],
		[TestAction.add_image, 'image3', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.delete_volume, 'volume3'],
		[TestAction.expunge_volume, 'volume3'],
		[TestAction.create_mini_vm, 'vm5', 'data_volume=true'],
		[TestAction.create_vm_backup, 'vm1', 'vm1-backup3'],
		[TestAction.migrate_vm, 'vm5'],
		[TestAction.delete_image, 'image3'],
		[TestAction.recover_image, 'image3'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.use_vm_backup, 'vm1-backup3'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.add_image, 'image4', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.attach_volume, 'vm2', 'volume5'],
		[TestAction.detach_volume, 'volume5'],
])



'''
The final status:
Running:['vm2', 'vm3', 'vm4', 'vm5', 'vm1']
Stopped:[]
Enadbled:['vm3-backup2', 'vm1-backup3', 'vm2-image2', 'image3', 'image4']
attached:[]
Detached:['volume1', 'volume2', 'volume4', 'volume5']
Deleted:['volume1-backup1']
Expunged:['volume3', 'image1']
Ha:[]
Group:
	vm_backup2:['vm1-backup3']---vm1_
	vm_backup1:['vm3-backup2']---vm3_
'''
