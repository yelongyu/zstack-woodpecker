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
		[TestAction.create_mini_vm, 'vm2', 'flag=thin'],
		[TestAction.resize_volume, 'vm1', 5*1024*1024],
		[TestAction.create_volume, 'volume2', 'flag=scsi'],
		[TestAction.attach_volume, 'vm1', 'volume2'],
		[TestAction.create_mini_vm, 'vm3', 'network=random'],
		[TestAction.delete_volume, 'volume1'],
		[TestAction.add_image, 'image1', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.recover_volume, 'volume1'],
		[TestAction.attach_volume, 'vm3', 'volume1'],
		[TestAction.stop_vm, 'vm3'],
		[TestAction.use_volume_backup, 'volume1-backup1'],
		[TestAction.start_vm, 'vm3'],
		[TestAction.detach_volume, 'volume1'],
		[TestAction.delete_image, 'image1'],
		[TestAction.recover_image, 'image1'],
		[TestAction.delete_image, 'image1'],
		[TestAction.expunge_image, 'image1'],
		[TestAction.create_volume_backup, 'volume2', 'volume2-backup2'],
		[TestAction.destroy_vm, 'vm1'],
		[TestAction.recover_vm, 'vm1'],
		[TestAction.create_image_from_volume, 'vm3', 'vm3-image2'],
		[TestAction.attach_volume, 'vm3', 'volume2'],
		[TestAction.detach_volume, 'volume2'],
		[TestAction.create_volume, 'volume3', 'flag=thick,scsi'],
		[TestAction.create_mini_vm, 'vm4', 'memory=random'],
		[TestAction.add_image, 'image3', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.delete_volume, 'volume2'],
		[TestAction.expunge_volume, 'volume2'],
		[TestAction.destroy_vm, 'vm2'],
		[TestAction.recover_vm, 'vm2'],
		[TestAction.create_vm_backup, 'vm3', 'vm3-backup3'],
		[TestAction.migrate_vm, 'vm4'],
		[TestAction.delete_image, 'image3'],
		[TestAction.recover_image, 'image3'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.create_vm_backup, 'vm1', 'vm1-backup4'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.use_vm_backup, 'vm1-backup4'],
		[TestAction.add_image, 'image4', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.attach_volume, 'vm3', 'volume3'],
		[TestAction.detach_volume, 'volume3'],
])



'''
The final status:
Running:['vm3', 'vm4']
Stopped:['vm2', 'vm1']
Enadbled:['volume1-backup1', 'volume2-backup2', 'vm3-backup3', 'vm1-backup4', 'vm3-image2', 'image3', 'image4']
attached:[]
Detached:['volume1', 'volume3']
Deleted:[]
Expunged:['volume2', 'image1']
Ha:[]
Group:
	vm_backup2:['vm1-backup4']---vm1_
	vm_backup1:['vm3-backup3']---vm3_
'''
