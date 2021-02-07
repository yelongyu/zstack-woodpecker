import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", path_list=[
		[TestAction.create_mini_vm, 'vm1', ],
		[TestAction.create_volume, 'volume1', 'flag=scsi'],
		[TestAction.attach_volume, 'vm1', 'volume1'],
		[TestAction.create_volume_backup, 'volume1', 'volume1-backup1'],
		[TestAction.detach_volume, 'volume1'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.resize_volume, 'vm1', 5*1024*1024],
		[TestAction.attach_volume, 'vm1', 'volume1'],
		[TestAction.detach_volume, 'volume1'],
		[TestAction.create_mini_vm, 'vm2', 'network=random'],
		[TestAction.delete_volume, 'volume1'],
		[TestAction.add_image, 'image1', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.create_vm_backup, 'vm2', 'vm2-backup2'],
		[TestAction.delete_vm_backup, 'vm2-backup2'],
		[TestAction.delete_image, 'image1'],
		[TestAction.expunge_image, 'image1'],
		[TestAction.create_volume, 'volume2', 'flag=scsi'],
		[TestAction.attach_volume, 'vm2', 'volume2'],
		[TestAction.create_volume_backup, 'volume2', 'volume2-backup3'],
		[TestAction.detach_volume, 'volume2'],
		[TestAction.create_mini_vm, 'vm3', 'data_volume=true'],
		[TestAction.create_image_from_volume, 'vm2', 'vm2-image2'],
		[TestAction.detach_volume, 'auto-volume3'],
		[TestAction.create_volume, 'volume4', 'flag=thick,scsi'],
		[TestAction.create_mini_vm, 'vm4', 'flag=thin'],
		[TestAction.add_image, 'image3', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.delete_volume, 'auto-volume3'],
		[TestAction.expunge_volume, 'auto-volume3'],
		[TestAction.reboot_vm, 'vm3'],
		[TestAction.attach_volume, 'vm3', 'volume4'],
		[TestAction.create_volume_backup, 'volume4', 'volume4-backup4'],
		[TestAction.detach_volume, 'volume4'],
		[TestAction.resize_data_volume, 'volume2', 5*1024*1024],
		[TestAction.delete_image, 'vm2-image2'],
		[TestAction.recover_image, 'vm2-image2'],
		[TestAction.create_vm_backup, 'vm4', 'vm4-backup5'],
		[TestAction.stop_vm, 'vm4'],
		[TestAction.use_vm_backup, 'vm4-backup5'],
		[TestAction.start_vm, 'vm4'],
		[TestAction.add_image, 'image4', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.attach_volume, 'vm3', 'volume2'],
])



'''
The final status:
Running:['vm1', 'vm2', 'vm3', 'vm4']
Stopped:[]
Enadbled:['volume1-backup1', 'volume2-backup3', 'volume4-backup4', 'vm4-backup5', 'image3', 'vm2-image2', 'image4']
attached:['volume2']
Detached:['volume4']
Deleted:['volume1', 'vm2-backup2']
Expunged:['auto-volume3', 'image1']
Ha:[]
Group:
	vm_backup1:['vm4-backup5']---vm4_
'''
