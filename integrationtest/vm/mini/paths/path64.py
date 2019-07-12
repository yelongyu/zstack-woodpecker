import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", path_list=[
		[TestAction.create_mini_vm, 'vm1', ],
		[TestAction.change_vm_ha, 'vm1'],
		[TestAction.create_vm_backup, 'vm1', 'vm1-backup1'],
		[TestAction.create_mini_vm, 'vm2', ],
		[TestAction.stop_vm, 'vm2'],
		[TestAction.start_vm, 'vm2'],
		[TestAction.resize_volume, 'vm1', 5*1024*1024],
		[TestAction.create_volume, 'volume1', 'flag=scsi'],
		[TestAction.attach_volume, 'vm1', 'volume1'],
		[TestAction.detach_volume, 'volume1'],
		[TestAction.create_mini_vm, 'vm3', 'network=random'],
		[TestAction.create_volume, 'volume2', 'flag=thin,scsi'],
		[TestAction.add_image, 'image1', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.attach_volume, 'vm2', 'volume1'],
		[TestAction.create_volume_backup, 'volume1', 'volume1-backup2'],
		[TestAction.delete_volume_backup, 'volume1-backup2'],
		[TestAction.detach_volume, 'volume1'],
		[TestAction.delete_image, 'image1'],
		[TestAction.expunge_image, 'image1'],
		[TestAction.create_vm_backup, 'vm2', 'vm2-backup3'],
		[TestAction.destroy_vm, 'vm1'],
		[TestAction.recover_vm, 'vm1'],
		[TestAction.resize_volume, 'vm1', 5*1024*1024],
		[TestAction.attach_volume, 'vm1', 'volume1'],
		[TestAction.create_volume, 'volume3', 'flag=thin,scsi'],
		[TestAction.stop_vm, 'vm2'],
		[TestAction.add_image, 'image2', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.delete_volume, 'volume3'],
		[TestAction.expunge_volume, 'volume3'],
		[TestAction.add_image, 'image3', 'root', os.environ.get('isoForVmUrl')],
		[TestAction.create_vm_by_image, 'image3', 'iso', 'vm4'],
		[TestAction.attach_volume, 'vm1', 'volume2'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.create_volume_backup, 'volume2', 'volume2-backup4'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.detach_volume, 'volume2'],
		[TestAction.create_image_from_volume, 'vm1', 'vm1-image4'],
		[TestAction.delete_image, 'vm1-image4'],
		[TestAction.attach_volume, 'vm2', 'volume2'],
		[TestAction.use_volume_backup, 'volume2-backup4'],
		[TestAction.detach_volume, 'volume2'],
		[TestAction.add_image, 'image5', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.create_volume, 'volume4', 'flag=scsi'],
		[TestAction.attach_volume, 'vm2', 'volume4'],
])



'''
The final status:
Running:['vm3', 'vm4']
Stopped:['vm2', 'vm1']
Enadbled:['vm1-backup1', 'vm2-backup3', 'volume2-backup4', 'image2', 'image3', 'image5']
attached:['volume1', 'volume4']
Detached:['volume2']
Deleted:['volume1-backup2', 'vm1-image4']
Expunged:['volume3', 'image1']
Ha:[]
Group:
	vm_backup2:['vm2-backup3']---vm2_
	vm_backup1:['vm1-backup1']---vm1_
'''
