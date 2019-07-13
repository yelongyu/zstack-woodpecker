import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", path_list=[
		[TestAction.create_mini_vm, 'vm1', ],
		[TestAction.destroy_vm, 'vm1'],
		[TestAction.create_mini_vm, 'vm2', ],
		[TestAction.create_vm_backup, 'vm2', 'vm2-backup1'],
		[TestAction.create_mini_vm, 'vm3', 'flag=thin'],
		[TestAction.create_volume, 'volume1', 'flag=scsi'],
		[TestAction.resize_data_volume, 'volume1', 5*1024*1024],
		[TestAction.create_volume, 'volume2', 'size=random', 'flag=scsi'],
		[TestAction.create_mini_vm, 'vm4', 'network=random'],
		[TestAction.create_volume, 'volume3', 'flag=thin,scsi'],
		[TestAction.add_image, 'image1', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.attach_volume, 'vm3', 'volume3'],
		[TestAction.create_volume_backup, 'volume3', 'volume3-backup2'],
		[TestAction.delete_volume_backup, 'volume3-backup2'],
		[TestAction.detach_volume, 'volume3'],
		[TestAction.delete_image, 'image1'],
		[TestAction.expunge_image, 'image1'],
		[TestAction.attach_volume, 'vm3', 'volume3'],
		[TestAction.create_volume_backup, 'volume3', 'volume3-backup3'],
		[TestAction.detach_volume, 'volume3'],
		[TestAction.create_mini_vm, 'vm5', 'data_volume=true'],
		[TestAction.resize_volume, 'vm4', 5*1024*1024],
		[TestAction.create_volume, 'volume4', 'flag=scsi'],
		[TestAction.attach_volume, 'vm2', 'volume4'],
		[TestAction.delete_volume, 'volume3'],
		[TestAction.recover_volume, 'volume3'],
		[TestAction.stop_vm, 'vm3'],
		[TestAction.start_vm, 'vm3'],
		[TestAction.add_image, 'image2', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.delete_volume, 'volume1'],
		[TestAction.expunge_volume, 'volume1'],
		[TestAction.reboot_vm, 'vm5'],
		[TestAction.attach_volume, 'vm5', 'volume2'],
		[TestAction.create_volume_backup, 'volume2', 'volume2-backup4'],
		[TestAction.detach_volume, 'volume2'],
		[TestAction.migrate_vm, 'vm5'],
		[TestAction.delete_image, 'image2'],
		[TestAction.attach_volume, 'vm5', 'volume2'],
		[TestAction.stop_vm, 'vm5'],
		[TestAction.use_volume_backup, 'volume2-backup4'],
		[TestAction.start_vm, 'vm5'],
		[TestAction.detach_volume, 'volume2'],
		[TestAction.add_image, 'image3', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.detach_volume, 'volume4'],
])



'''
The final status:
Running:['vm2', 'vm4', 'vm3', 'vm5']
Stopped:[]
Enadbled:['vm2-backup1', 'volume3-backup3', 'volume2-backup4', 'image3']
attached:[]
Detached:['volume3', 'volume2', 'volume4']
Deleted:['vm1', 'volume3-backup2', 'image2']
Expunged:['volume1', 'image1']
Ha:[]
Group:
	vm_backup1:['vm2-backup1']---vm2_
'''
