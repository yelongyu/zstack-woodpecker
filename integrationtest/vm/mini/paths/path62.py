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
		[TestAction.create_mini_vm, 'vm2', 'cpu=random'],
		[TestAction.resize_volume, 'vm1', 5*1024*1024],
		[TestAction.create_volume, 'volume2', 'size=random', 'flag=scsi'],
		[TestAction.create_mini_vm, 'vm3', 'network=random'],
		[TestAction.delete_volume, 'volume2'],
		[TestAction.recover_volume, 'volume2'],
		[TestAction.add_image, 'image1', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.delete_volume_backup, 'volume1-backup1'],
		[TestAction.delete_image, 'image1'],
		[TestAction.recover_image, 'image1'],
		[TestAction.delete_image, 'image1'],
		[TestAction.expunge_image, 'image1'],
		[TestAction.create_vm_backup, 'vm2', 'vm2-backup2'],
		[TestAction.add_image, 'image2', 'root', os.environ.get('isoForVmUrl')],
		[TestAction.create_vm_by_image, 'image2', 'iso', 'vm4'],
		[TestAction.resize_data_volume, 'volume1', 5*1024*1024],
		[TestAction.attach_volume, 'vm3', 'volume2'],
		[TestAction.detach_volume, 'volume2'],
		[TestAction.create_volume, 'volume3', 'flag=thin,scsi'],
		[TestAction.create_mini_vm, 'vm5', 'flag=thin'],
		[TestAction.add_image, 'image3', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.delete_volume, 'volume1'],
		[TestAction.expunge_volume, 'volume1'],
		[TestAction.destroy_vm, 'vm2'],
		[TestAction.create_vm_backup, 'vm4', 'vm4-backup3'],
		[TestAction.resize_volume, 'vm5', 5*1024*1024],
		[TestAction.delete_image, 'image3'],
		[TestAction.recover_image, 'image3'],
		[TestAction.attach_volume, 'vm5', 'volume3'],
		[TestAction.create_volume_backup, 'volume3', 'volume3-backup4'],
		[TestAction.stop_vm, 'vm5'],
		[TestAction.use_volume_backup, 'volume3-backup4'],
		[TestAction.start_vm, 'vm5'],
		[TestAction.detach_volume, 'volume3'],
		[TestAction.add_image, 'image4', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.attach_volume, 'vm1', 'volume2'],
])



'''
The final status:
Running:['vm1', 'vm3', 'vm4', 'vm5']
Stopped:[]
Enadbled:['vm2-backup2', 'vm4-backup3', 'volume3-backup4', 'image2', 'image3', 'image4']
attached:['volume2']
Detached:['volume3']
Deleted:['vm2', 'volume1-backup1']
Expunged:['volume1', 'image1']
Ha:[]
Group:
	vm_backup2:['vm4-backup3']---vm4_
	vm_backup1:['vm2-backup2']---vm2_
'''
