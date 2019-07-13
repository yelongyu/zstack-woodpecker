import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", path_list=[
		[TestAction.create_mini_vm, 'vm1', ],
		[TestAction.reboot_vm, 'vm1'],
		[TestAction.create_volume, 'volume1', 'flag=scsi'],
		[TestAction.attach_volume, 'vm1', 'volume1'],
		[TestAction.create_volume_backup, 'volume1', 'volume1-backup1'],
		[TestAction.detach_volume, 'volume1'],
		[TestAction.create_mini_vm, 'vm2', 'memory=random'],
		[TestAction.resize_volume, 'vm2', 5*1024*1024],
		[TestAction.create_volume, 'volume2', 'flag=scsi'],
		[TestAction.attach_volume, 'vm2', 'volume1'],
		[TestAction.create_mini_vm, 'vm3', 'network=random'],
		[TestAction.create_volume, 'volume3', 'flag=thin,scsi'],
		[TestAction.add_image, 'image1', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.create_vm_backup, 'vm2', 'vm2-backup2'],
		[TestAction.stop_vm, 'vm2'],
		[TestAction.use_vm_backup, 'vm2-backup2'],
		[TestAction.start_vm, 'vm2'],
		[TestAction.delete_image, 'image1'],
		[TestAction.expunge_image, 'image1'],
		[TestAction.attach_volume, 'vm3', 'volume3'],
		[TestAction.create_volume_backup, 'volume3', 'volume3-backup4'],
		[TestAction.detach_volume, 'volume3'],
		[TestAction.destroy_vm, 'vm2'],
		[TestAction.migrate_vm, 'vm3'],
		[TestAction.attach_volume, 'vm1', 'volume3'],
		[TestAction.delete_volume, 'volume1'],
		[TestAction.create_mini_vm, 'vm4', 'cpu=random'],
		[TestAction.add_image, 'image2', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.delete_volume, 'volume2'],
		[TestAction.expunge_volume, 'volume2'],
		[TestAction.create_mini_vm, 'vm5', 'data_volume=true'],
		[TestAction.create_volume_backup, 'volume3', 'volume3-backup5'],
		[TestAction.migrate_vm, 'vm5'],
		[TestAction.delete_image, 'image2'],
		[TestAction.recover_image, 'image2'],
		[TestAction.create_vm_backup, 'vm3', 'vm3-backup6'],
		[TestAction.stop_vm, 'vm3'],
		[TestAction.use_vm_backup, 'vm3-backup6'],
		[TestAction.start_vm, 'vm3'],
		[TestAction.add_image, 'image3', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.create_volume, 'volume4', 'flag=scsi'],
		[TestAction.attach_volume, 'vm1', 'volume4'],
])



'''
The final status:
Running:['vm1', 'vm4', 'vm5', 'vm3']
Stopped:[]
Enadbled:['volume1-backup1', 'vm2-backup2', 'volume1-backup2', 'volume3-backup4', 'volume3-backup5', 'vm3-backup6', 'image2', 'image3']
attached:['volume3', 'volume4']
Detached:[]
Deleted:['vm2', 'volume1']
Expunged:['volume2', 'image1']
Ha:[]
Group:
	vm_backup2:['vm3-backup6']---vm3_
	vm_backup1:['vm2-backup2', 'volume1-backup2']---vm2_volume1
'''
