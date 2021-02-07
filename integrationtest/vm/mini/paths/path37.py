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
		[TestAction.destroy_vm, 'vm1'],
		[TestAction.expunge_vm, 'vm1'],
		[TestAction.create_mini_vm, 'vm2', ],
		[TestAction.create_image_from_volume, 'vm2', 'vm2-image1'],
		[TestAction.create_volume, 'volume2', 'size=random', 'flag=scsi'],
		[TestAction.create_mini_vm, 'vm3', 'network=random'],
		[TestAction.create_volume, 'volume3', 'flag=thick,scsi'],
		[TestAction.add_image, 'image2', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.attach_volume, 'vm2', 'volume1'],
		[TestAction.stop_vm, 'vm2'],
		[TestAction.use_volume_backup, 'volume1-backup1'],
		[TestAction.start_vm, 'vm2'],
		[TestAction.detach_volume, 'volume1'],
		[TestAction.delete_image, 'vm2-image1'],
		[TestAction.recover_image, 'vm2-image1'],
		[TestAction.delete_image, 'image2'],
		[TestAction.expunge_image, 'image2'],
		[TestAction.attach_volume, 'vm3', 'volume3'],
		[TestAction.create_volume_backup, 'volume3', 'volume3-backup2'],
		[TestAction.detach_volume, 'volume3'],
		[TestAction.change_vm_ha, 'vm3'],
		[TestAction.create_image_from_volume, 'vm3', 'vm3-image3'],
		[TestAction.create_volume, 'volume4', 'size=random', 'flag=scsi'],
		[TestAction.create_volume, 'volume5', 'flag=thin,scsi'],
		[TestAction.stop_vm, 'vm2'],
		[TestAction.add_image, 'image4', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.delete_volume, 'volume4'],
		[TestAction.expunge_volume, 'volume4'],
		[TestAction.destroy_vm, 'vm3'],
		[TestAction.recover_vm, 'vm3'],
		[TestAction.start_vm, 'vm3'],
		[TestAction.create_vm_backup, 'vm3', 'vm3-backup3'],
		[TestAction.stop_vm, 'vm3'],
		[TestAction.start_vm, 'vm2'],
		[TestAction.migrate_vm, 'vm2'],
		[TestAction.delete_image, 'image4'],
		[TestAction.delete_volume_backup, 'volume1-backup1'],
		[TestAction.add_image, 'image5', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.attach_volume, 'vm2', 'volume5'],
])



'''
The final status:
Running:['vm2']
Stopped:['vm3']
Enadbled:['volume3-backup2', 'vm3-backup3', 'vm2-image1', 'vm3-image3', 'image5']
attached:['volume5']
Detached:['volume2', 'volume1', 'volume3']
Deleted:['volume1-backup1', 'image4']
Expunged:['vm1', 'volume4', 'image2']
Ha:[]
Group:
	vm_backup1:['vm3-backup3']---vm3_
'''
