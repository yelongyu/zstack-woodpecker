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
		[TestAction.stop_vm, 'vm2'],
		[TestAction.resize_volume, 'vm2', 5*1024*1024],
		[TestAction.attach_volume, 'vm2', 'volume1'],
		[TestAction.create_mini_vm, 'vm3', 'network=random'],
		[TestAction.create_volume, 'volume2', 'flag=thick,scsi'],
		[TestAction.add_image, 'image1', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.start_vm, 'vm2'],
		[TestAction.create_vm_backup, 'vm2', 'vm2-backup2'],
		[TestAction.stop_vm, 'vm2'],
		[TestAction.use_vm_backup, 'vm2-backup2'],
		[TestAction.delete_image, 'image1'],
		[TestAction.recover_image, 'image1'],
		[TestAction.delete_image, 'image1'],
		[TestAction.expunge_image, 'image1'],
		[TestAction.create_vm_backup, 'vm3', 'vm3-backup4'],
		[TestAction.recover_vm, 'vm1'],
		[TestAction.resize_volume, 'vm3', 5*1024*1024],
		[TestAction.attach_volume, 'vm3', 'volume2'],
		[TestAction.create_volume, 'volume3', 'flag=thin,scsi'],
		[TestAction.create_mini_vm, 'vm4', 'flag=thin'],
		[TestAction.add_image, 'image2', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.delete_volume, 'volume1'],
		[TestAction.expunge_volume, 'volume1'],
		[TestAction.create_mini_vm, 'vm5', 'data_volume=true'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.create_vm_backup, 'vm1', 'vm1-backup5'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.resize_data_volume, 'volume3', 5*1024*1024],
		[TestAction.delete_image, 'image2'],
		[TestAction.recover_image, 'image2'],
		[TestAction.create_volume_backup, 'volume2', 'volume2-backup6'],
		[TestAction.stop_vm, 'vm3'],
		[TestAction.use_volume_backup, 'volume2-backup6'],
		[TestAction.start_vm, 'vm3'],
		[TestAction.add_image, 'image3', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.create_volume, 'volume4', 'flag=scsi'],
		[TestAction.attach_volume, 'vm5', 'volume3'],
])



'''
The final status:
Running:['vm4', 'vm5', 'vm3']
Stopped:['vm2', 'vm1']
Enadbled:['volume1-backup1', 'vm2-backup2', 'volume1-backup2', 'vm3-backup4', 'vm1-backup5', 'volume2-backup6', 'image2', 'image3']
attached:['volume2', 'volume3']
Detached:['volume4']
Deleted:[]
Expunged:['volume1', 'image1']
Ha:[]
Group:
	vm_backup2:['vm3-backup4']---vm3_
	vm_backup3:['vm1-backup5']---vm1_
	vm_backup1:['vm2-backup2', 'volume1-backup2']---vm2_volume1
'''
