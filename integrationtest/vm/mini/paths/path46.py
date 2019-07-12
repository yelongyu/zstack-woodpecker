import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", path_list=[
		[TestAction.create_mini_vm, 'vm1', ],
		[TestAction.reboot_vm, 'vm1'],
		[TestAction.create_vm_backup, 'vm1', 'vm1-backup1'],
		[TestAction.create_mini_vm, 'vm2', 'flag=thin'],
		[TestAction.create_volume, 'volume1', 'flag=scsi'],
		[TestAction.resize_data_volume, 'volume1', 5*1024*1024],
		[TestAction.create_volume, 'volume2', 'size=random', 'flag=scsi'],
		[TestAction.create_mini_vm, 'vm3', 'network=random'],
		[TestAction.create_volume, 'volume3', 'flag=thick,scsi'],
		[TestAction.add_image, 'image1', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.delete_vm_backup, 'vm1-backup1'],
		[TestAction.delete_image, 'image1'],
		[TestAction.expunge_image, 'image1'],
		[TestAction.create_vm_backup, 'vm2', 'vm2-backup2'],
		[TestAction.create_mini_vm, 'vm4', ],
		[TestAction.resize_data_volume, 'volume3', 5*1024*1024],
		[TestAction.create_volume, 'volume4', 'flag=scsi'],
		[TestAction.attach_volume, 'vm1', 'volume2'],
		[TestAction.create_volume, 'volume5', 'flag=thin,scsi'],
		[TestAction.create_mini_vm, 'vm5', 'flag=thin'],
		[TestAction.add_image, 'image2', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.delete_volume, 'volume5'],
		[TestAction.expunge_volume, 'volume5'],
		[TestAction.destroy_vm, 'vm1'],
		[TestAction.recover_vm, 'vm1'],
		[TestAction.attach_volume, 'vm5', 'volume4'],
		[TestAction.create_volume_backup, 'volume4', 'volume4-backup3'],
		[TestAction.detach_volume, 'volume4'],
		[TestAction.resize_volume, 'vm2', 5*1024*1024],
		[TestAction.delete_image, 'image2'],
		[TestAction.recover_image, 'image2'],
		[TestAction.attach_volume, 'vm5', 'volume4'],
		[TestAction.stop_vm, 'vm5'],
		[TestAction.use_volume_backup, 'volume4-backup3'],
		[TestAction.start_vm, 'vm5'],
		[TestAction.detach_volume, 'volume4'],
		[TestAction.add_image, 'image3', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.attach_volume, 'vm2', 'volume4'],
])



'''
The final status:
Running:['vm2', 'vm3', 'vm4', 'vm5']
Stopped:['vm1']
Enadbled:['vm2-backup2', 'volume4-backup3', 'image2', 'image3']
attached:['volume4']
Detached:['volume1', 'volume3', 'volume2']
Deleted:['vm1-backup1']
Expunged:['volume5', 'image1']
Ha:[]
Group:
	vm_backup1:['vm2-backup2']---vm2_
'''
