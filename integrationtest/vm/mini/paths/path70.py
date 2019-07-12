import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", path_list=[
		[TestAction.create_mini_vm, 'vm1', ],
		[TestAction.create_vm_backup, 'vm1', 'vm1-backup1'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.resize_volume, 'vm1', 5*1024*1024],
		[TestAction.create_volume, 'volume1', 'flag=scsi'],
		[TestAction.attach_volume, 'vm1', 'volume1'],
		[TestAction.create_mini_vm, 'vm2', 'network=random'],
		[TestAction.create_volume, 'volume2', 'flag=thin,scsi'],
		[TestAction.add_image, 'image1', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.attach_volume, 'vm2', 'volume2'],
		[TestAction.create_volume_backup, 'volume2', 'volume2-backup2'],
		[TestAction.delete_volume_backup, 'volume2-backup2'],
		[TestAction.detach_volume, 'volume2'],
		[TestAction.delete_image, 'image1'],
		[TestAction.expunge_image, 'image1'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.create_vm_backup, 'vm1', 'vm1-backup3'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.destroy_vm, 'vm1'],
		[TestAction.resize_volume, 'vm2', 5*1024*1024],
		[TestAction.attach_volume, 'vm2', 'volume1'],
		[TestAction.create_volume, 'volume3', 'flag=thin,scsi'],
		[TestAction.stop_vm, 'vm2'],
		[TestAction.add_image, 'image2', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.delete_volume, 'volume3'],
		[TestAction.expunge_volume, 'volume3'],
		[TestAction.destroy_vm, 'vm2'],
		[TestAction.create_mini_vm, 'vm3', ],
		[TestAction.create_vm_backup, 'vm3', 'vm3-backup5'],
		[TestAction.resize_data_volume, 'volume1', 5*1024*1024],
		[TestAction.delete_image, 'image2'],
		[TestAction.delete_vm_backup, 'vm3-backup5'],
		[TestAction.add_image, 'image3', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.attach_volume, 'vm3', 'volume2'],
		[TestAction.detach_volume, 'volume2'],
])



'''
The final status:
Running:['vm3']
Stopped:[]
Enadbled:['vm1-backup1', 'vm1-backup3', 'volume1-backup3', 'image3']
attached:[]
Detached:['volume1', 'volume2']
Deleted:['vm1', 'vm2', 'volume2-backup2', 'vm3-backup5', 'image2']
Expunged:['volume3', 'image1']
Ha:[]
Group:
	vm_backup2:['vm1-backup3', 'volume1-backup3']---vm1_volume1
	vm_backup1:['vm1-backup1']---vm1_
'''
