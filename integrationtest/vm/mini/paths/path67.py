import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", path_list=[
		[TestAction.create_mini_vm, 'vm1', 'data_volume=true'],
		[TestAction.create_vm_backup, 'vm1', 'vm1-backup1'],
		[TestAction.destroy_vm, 'vm1'],
		[TestAction.expunge_vm, 'vm1'],
		[TestAction.create_mini_vm, 'vm2', ],
		[TestAction.migrate_vm, 'vm2'],
		[TestAction.create_volume, 'volume1', 'flag=scsi'],
		[TestAction.attach_volume, 'vm2', 'volume1'],
		[TestAction.create_mini_vm, 'vm3', 'network=random'],
		[TestAction.delete_volume, 'volume1'],
		[TestAction.add_image, 'image1', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.create_vm_backup, 'vm3', 'vm3-backup2'],
		[TestAction.delete_vm_backup, 'vm3-backup2'],
		[TestAction.delete_image, 'image1'],
		[TestAction.expunge_image, 'image1'],
		[TestAction.create_vm_backup, 'vm3', 'vm3-backup3'],
		[TestAction.create_mini_vm, 'vm4', ],
		[TestAction.migrate_vm, 'vm4'],
		[TestAction.create_volume, 'volume2', 'flag=scsi'],
		[TestAction.attach_volume, 'vm4', 'volume2'],
		[TestAction.delete_volume, 'volume2'],
		[TestAction.create_mini_vm, 'vm5', 'flag=thin'],
		[TestAction.add_image, 'image2', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.create_volume, 'volume3', 'flag=scsi'],
		[TestAction.delete_volume, 'volume3'],
		[TestAction.expunge_volume, 'volume3'],
		[TestAction.create_mini_vm, 'vm6', ],
		[TestAction.create_volume, 'volume4', 'flag=scsi'],
		[TestAction.attach_volume, 'vm3', 'volume4'],
		[TestAction.create_volume_backup, 'volume4', 'volume4-backup4'],
		[TestAction.detach_volume, 'volume4'],
		[TestAction.migrate_vm, 'vm6'],
		[TestAction.delete_image, 'image2'],
		[TestAction.delete_volume_backup, 'volume4-backup4'],
		[TestAction.add_image, 'image3', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.attach_volume, 'vm2', 'volume4'],
])



'''
The final status:
Running:['vm2', 'vm3', 'vm4', 'vm5', 'vm6']
Stopped:[]
Enadbled:['vm1-backup1', 'vm3-backup3', 'image3']
attached:['volume4']
Detached:[]
Deleted:['volume1', 'volume2', 'vm3-backup2', 'volume4-backup4', 'image2']
Expunged:['vm1', 'volume3', 'image1']
Ha:[]
Group:
	vm_backup2:['vm3-backup3']---vm3_
	vm_backup1:['vm1-backup1']---vm1_
'''
