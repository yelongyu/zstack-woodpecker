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
		[TestAction.stop_vm, 'vm1'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.migrate_vm, 'vm1'],
		[TestAction.create_volume, 'volume2', 'size=random', 'flag=scsi'],
		[TestAction.create_mini_vm, 'vm2', 'network=random'],
		[TestAction.create_volume, 'volume3', 'flag=thin,scsi'],
		[TestAction.add_image, 'image2', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.create_vm_backup, 'vm1', 'vm1-backup2'],
		[TestAction.delete_vm_backup, 'vm1-backup2'],
		[TestAction.delete_image, 'image2'],
		[TestAction.recover_image, 'image2'],
		[TestAction.delete_image, 'image1'],
		[TestAction.expunge_image, 'image1'],
		[TestAction.attach_volume, 'vm2', 'volume2'],
		[TestAction.create_volume_backup, 'volume2', 'volume2-backup3'],
		[TestAction.detach_volume, 'volume2'],
		[TestAction.create_mini_vm, 'vm3', ],
		[TestAction.create_image_from_volume, 'vm1', 'vm1-image3'],
		[TestAction.create_volume, 'volume4', 'size=random', 'flag=scsi'],
		[TestAction.delete_volume, 'volume2'],
		[TestAction.create_mini_vm, 'vm4', 'cpu=random'],
		[TestAction.add_image, 'image4', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.delete_volume, 'volume1'],
		[TestAction.expunge_volume, 'volume1'],
		[TestAction.change_vm_ha, 'vm2'],
		[TestAction.create_vm_backup, 'vm1', 'vm1-backup4'],
		[TestAction.resize_data_volume, 'volume4', 5*1024*1024],
		[TestAction.delete_image, 'vm1-image3'],
		[TestAction.recover_volume, 'volume2'],
		[TestAction.attach_volume, 'vm4', 'volume2'],
		[TestAction.stop_vm, 'vm4'],
		[TestAction.use_volume_backup, 'volume2-backup3'],
		[TestAction.start_vm, 'vm4'],
		[TestAction.detach_volume, 'volume2'],
		[TestAction.add_image, 'image5', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.attach_volume, 'vm3', 'volume2'],
])



'''
The final status:
Running:['vm1', 'vm2', 'vm3', 'vm4']
Stopped:[]
Enadbled:['volume1-backup1', 'volume2-backup3', 'vm1-backup4', 'image2', 'image4', 'image5']
attached:['volume2']
Detached:['volume3', 'volume4']
Deleted:['vm1-backup2', 'vm1-image3']
Expunged:['volume1', 'image1']
Ha:['vm2']
Group:
	vm_backup1:['vm1-backup4']---vm1_
'''
