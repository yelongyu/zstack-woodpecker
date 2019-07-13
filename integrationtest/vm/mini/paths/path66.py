import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", path_list=[
		[TestAction.create_mini_vm, 'vm1', ],
		[TestAction.destroy_vm, 'vm1'],
		[TestAction.create_volume, 'volume1', 'flag=scsi'],
		[TestAction.create_mini_vm, 'vm2', ],
		[TestAction.attach_volume, 'vm2', 'volume1'],
		[TestAction.create_volume_backup, 'volume1', 'volume1-backup1'],
		[TestAction.detach_volume, 'volume1'],
		[TestAction.create_mini_vm, 'vm3', 'cpu=random'],
		[TestAction.resize_volume, 'vm2', 5*1024*1024],
		[TestAction.attach_volume, 'vm2', 'volume1'],
		[TestAction.create_mini_vm, 'vm4', 'network=random'],
		[TestAction.delete_volume, 'volume1'],
		[TestAction.add_image, 'image1', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.create_vm_backup, 'vm4', 'vm4-backup2'],
		[TestAction.delete_vm_backup, 'vm4-backup2'],
		[TestAction.delete_image, 'image1'],
		[TestAction.expunge_image, 'image1'],
		[TestAction.create_vm_backup, 'vm4', 'vm4-backup3'],
		[TestAction.destroy_vm, 'vm2'],
		[TestAction.create_volume, 'volume2', 'flag=scsi'],
		[TestAction.resize_data_volume, 'volume2', 5*1024*1024],
		[TestAction.attach_volume, 'vm4', 'volume2'],
		[TestAction.detach_volume, 'volume2'],
		[TestAction.create_volume, 'volume3', 'flag=thick,scsi'],
		[TestAction.destroy_vm, 'vm3'],
		[TestAction.expunge_vm, 'vm3'],
		[TestAction.add_image, 'image2', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.delete_volume, 'volume2'],
		[TestAction.expunge_volume, 'volume2'],
		[TestAction.add_image, 'image3', 'root', os.environ.get('isoForVmUrl')],
		[TestAction.create_vm_by_image, 'image3', 'iso', 'vm5'],
		[TestAction.create_vm_backup, 'vm5', 'vm5-backup4'],
		[TestAction.resize_volume, 'vm4', 5*1024*1024],
		[TestAction.delete_image, 'image2'],
		[TestAction.delete_vm_backup, 'vm4-backup3'],
		[TestAction.add_image, 'image4', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.create_volume, 'volume4', 'size=random', 'flag=scsi'],
])



'''
The final status:
Running:['vm4', 'vm5']
Stopped:[]
Enadbled:['volume1-backup1', 'vm5-backup4', 'image3', 'image4']
attached:[]
Detached:['volume3', 'volume4']
Deleted:['vm1', 'vm2', 'volume1', 'vm4-backup2', 'vm4-backup3', 'image2']
Expunged:['vm3', 'volume2', 'image1']
Ha:[]
Group:
	vm_backup2:['vm5-backup4']---vm5_
'''
