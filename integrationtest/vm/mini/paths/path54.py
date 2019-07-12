import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", path_list=[
		[TestAction.add_image, 'image1', 'root', os.environ.get('isoForVmUrl')],
		[TestAction.create_vm_by_image, 'image1', 'iso', 'vm1'],
		[TestAction.create_volume, 'volume1', 'flag=scsi'],
		[TestAction.attach_volume, 'vm1', 'volume1'],
		[TestAction.create_volume_backup, 'volume1', 'volume1-backup1'],
		[TestAction.detach_volume, 'volume1'],
		[TestAction.create_mini_vm, 'vm2', 'memory=random'],
		[TestAction.resize_data_volume, 'volume1', 5*1024*1024],
		[TestAction.attach_volume, 'vm2', 'volume1'],
		[TestAction.create_mini_vm, 'vm3', 'network=random'],
		[TestAction.create_volume, 'volume2', 'flag=thin,scsi'],
		[TestAction.add_image, 'image2', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.stop_vm, 'vm2'],
		[TestAction.use_volume_backup, 'volume1-backup1'],
		[TestAction.start_vm, 'vm2'],
		[TestAction.delete_image, 'image2'],
		[TestAction.recover_image, 'image2'],
		[TestAction.delete_image, 'image2'],
		[TestAction.expunge_image, 'image2'],
		[TestAction.create_vm_backup, 'vm1', 'vm1-backup2'],
		[TestAction.reboot_vm, 'vm2'],
		[TestAction.resize_data_volume, 'volume2', 5*1024*1024],
		[TestAction.create_volume, 'volume3', 'size=random', 'flag=scsi'],
		[TestAction.delete_volume, 'volume3'],
		[TestAction.stop_vm, 'vm3'],
		[TestAction.add_image, 'image3', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.delete_volume, 'volume1'],
		[TestAction.expunge_volume, 'volume1'],
		[TestAction.reboot_vm, 'vm2'],
		[TestAction.create_vm_backup, 'vm2', 'vm2-backup3'],
		[TestAction.resize_volume, 'vm3', 5*1024*1024],
		[TestAction.delete_image, 'image1'],
		[TestAction.delete_vm_backup, 'vm2-backup3'],
		[TestAction.add_image, 'image4', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.create_volume, 'volume4', 'flag=scsi'],
		[TestAction.attach_volume, 'vm2', 'volume2'],
])



'''
The final status:
Running:['vm1', 'vm2']
Stopped:['vm3']
Enadbled:['volume1-backup1', 'vm1-backup2', 'image3', 'image4']
attached:['volume2']
Detached:['volume4']
Deleted:['volume3', 'vm2-backup3', 'image1']
Expunged:['volume1', 'image2']
Ha:[]
Group:
	vm_backup1:['vm1-backup2']---vm1_
'''
