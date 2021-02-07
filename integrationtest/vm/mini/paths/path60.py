import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", path_list=[
		[TestAction.create_mini_vm, 'vm1', ],
		[TestAction.reboot_vm, 'vm1'],
		[TestAction.create_vm_backup, 'vm1', 'vm1-backup1'],
		[TestAction.create_mini_vm, 'vm2', 'flag=thin'],
		[TestAction.migrate_vm, 'vm1'],
		[TestAction.create_volume, 'volume1', 'flag=scsi'],
		[TestAction.attach_volume, 'vm2', 'volume1'],
		[TestAction.create_mini_vm, 'vm3', 'network=random'],
		[TestAction.delete_volume, 'volume1'],
		[TestAction.recover_volume, 'volume1'],
		[TestAction.add_image, 'image1', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.delete_vm_backup, 'vm1-backup1'],
		[TestAction.delete_image, 'image1'],
		[TestAction.recover_image, 'image1'],
		[TestAction.delete_image, 'image1'],
		[TestAction.expunge_image, 'image1'],
		[TestAction.attach_volume, 'vm2', 'volume1'],
		[TestAction.create_volume_backup, 'volume1', 'volume1-backup2'],
		[TestAction.detach_volume, 'volume1'],
		[TestAction.create_mini_vm, 'vm4', 'data_volume=true'],
		[TestAction.resize_data_volume, 'volume1', 5*1024*1024],
		[TestAction.create_volume, 'volume2', 'size=random', 'flag=scsi'],
		[TestAction.create_volume, 'volume3', 'flag=thick,scsi'],
		[TestAction.create_mini_vm, 'vm5', 'flag=thick'],
		[TestAction.add_image, 'image2', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.delete_volume, 'volume1'],
		[TestAction.expunge_volume, 'volume1'],
		[TestAction.change_vm_ha, 'vm5'],
		[TestAction.create_vm_backup, 'vm5', 'vm5-backup3'],
		[TestAction.resize_volume, 'vm1', 5*1024*1024],
		[TestAction.delete_image, 'image2'],
		[TestAction.recover_image, 'image2'],
		[TestAction.create_vm_backup, 'vm3', 'vm3-backup4'],
		[TestAction.stop_vm, 'vm3'],
		[TestAction.use_vm_backup, 'vm3-backup4'],
		[TestAction.start_vm, 'vm3'],
		[TestAction.add_image, 'image3', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.create_volume, 'volume4', 'size=random', 'flag=scsi'],
])



'''
The final status:
Running:['vm1', 'vm2', 'vm4', 'vm5', 'vm3']
Stopped:[]
Enadbled:['volume1-backup2', 'vm5-backup3', 'vm3-backup4', 'image2', 'image3']
attached:[]
Detached:['volume2', 'volume3', 'volume4']
Deleted:['vm1-backup1']
Expunged:['volume1', 'image1']
Ha:['vm5']
Group:
	vm_backup2:['vm3-backup4']---vm3_
	vm_backup1:['vm5-backup3']---vm5_
'''
