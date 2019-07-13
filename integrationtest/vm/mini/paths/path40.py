import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", path_list=[
		[TestAction.create_mini_vm, 'vm1', ],
		[TestAction.create_vm_backup, 'vm1', 'vm1-backup1'],
		[TestAction.destroy_vm, 'vm1'],
		[TestAction.expunge_vm, 'vm1'],
		[TestAction.create_volume, 'volume1', 'flag=scsi'],
		[TestAction.resize_data_volume, 'volume1', 5*1024*1024],
		[TestAction.create_volume, 'volume2', 'flag=scsi'],
		[TestAction.create_mini_vm, 'vm2', ],
		[TestAction.attach_volume, 'vm2', 'volume1'],
		[TestAction.create_mini_vm, 'vm3', 'network=random'],
		[TestAction.create_volume, 'volume3', 'flag=thin,scsi'],
		[TestAction.add_image, 'image1', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.attach_volume, 'vm2', 'volume2'],
		[TestAction.create_volume_backup, 'volume2', 'volume2-backup2'],
		[TestAction.delete_volume_backup, 'volume2-backup2'],
		[TestAction.detach_volume, 'volume2'],
		[TestAction.delete_image, 'image1'],
		[TestAction.expunge_image, 'image1'],
		[TestAction.create_vm_backup, 'vm2', 'vm2-backup3'],
		[TestAction.add_image, 'image2', 'root', os.environ.get('isoForVmUrl')],
		[TestAction.create_vm_by_image, 'image2', 'iso', 'vm4'],
		[TestAction.resize_volume, 'vm4', 5*1024*1024],
		[TestAction.attach_volume, 'vm2', 'volume2'],
		[TestAction.delete_volume, 'volume1'],
		[TestAction.recover_volume, 'volume1'],
		[TestAction.create_mini_vm, 'vm5', 'flag=thick'],
		[TestAction.add_image, 'image3', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.delete_volume, 'volume2'],
		[TestAction.expunge_volume, 'volume2'],
		[TestAction.create_vm_by_image, 'image2', 'iso', 'vm6'],
		[TestAction.create_vm_backup, 'vm6', 'vm6-backup5'],
		[TestAction.create_image_from_volume, 'vm4', 'vm4-image4'],
		[TestAction.delete_image, 'vm4-image4'],
		[TestAction.recover_image, 'vm4-image4'],
		[TestAction.attach_volume, 'vm3', 'volume1'],
		[TestAction.create_volume_backup, 'volume1', 'volume1-backup6'],
		[TestAction.stop_vm, 'vm3'],
		[TestAction.use_volume_backup, 'volume1-backup6'],
		[TestAction.start_vm, 'vm3'],
		[TestAction.detach_volume, 'volume1'],
		[TestAction.add_image, 'image5', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.create_volume, 'volume4', 'size=random', 'flag=scsi'],
])



'''
The final status:
Running:['vm2', 'vm4', 'vm5', 'vm6', 'vm3']
Stopped:[]
Enadbled:['vm1-backup1', 'vm2-backup3', 'volume1-backup3', 'vm6-backup5', 'volume1-backup6', 'image2', 'image3', 'vm4-image4', 'image5']
attached:[]
Detached:['volume3', 'volume1', 'volume4']
Deleted:['volume2-backup2']
Expunged:['vm1', 'volume2', 'image1']
Ha:[]
Group:
	vm_backup2:['vm2-backup3', 'volume1-backup3']---vm2_volume1
	vm_backup3:['vm6-backup5']---vm6_
	vm_backup1:['vm1-backup1']---vm1_
'''
