import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", path_list=[
		[TestAction.create_mini_vm, 'vm1', 'data_volume=true'],
		[TestAction.create_volume, 'volume1', 'flag=scsi'],
		[TestAction.attach_volume, 'vm1', 'volume1'],
		[TestAction.create_volume_backup, 'volume1', 'volume1-backup1'],
		[TestAction.detach_volume, 'volume1'],
		[TestAction.create_mini_vm, 'vm2', 'memory=random'],
		[TestAction.create_image_from_volume, 'vm2', 'vm2-image1'],
		[TestAction.attach_volume, 'vm2', 'volume1'],
		[TestAction.create_mini_vm, 'vm3', 'network=random'],
		[TestAction.create_volume, 'volume2', 'flag=thick,scsi'],
		[TestAction.add_image, 'image2', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.create_vm_backup, 'vm2', 'vm2-backup2'],
		[TestAction.stop_vm, 'vm2'],
		[TestAction.use_vm_backup, 'vm2-backup2'],
		[TestAction.start_vm, 'vm2'],
		[TestAction.delete_image, 'vm2-image1'],
		[TestAction.recover_image, 'vm2-image1'],
		[TestAction.delete_image, 'image2'],
		[TestAction.expunge_image, 'image2'],
		[TestAction.create_volume_backup, 'volume1', 'volume1-backup4'],
		[TestAction.create_mini_vm, 'vm4', ],
		[TestAction.migrate_vm, 'vm4'],
		[TestAction.detach_volume, 'volume1'],
		[TestAction.delete_volume, 'volume2'],
		[TestAction.add_image, 'image3', 'root', os.environ.get('isoForVmUrl')],
		[TestAction.create_vm_by_image, 'image3', 'iso', 'vm5'],
		[TestAction.attach_volume, 'vm5', 'volume1'],
		[TestAction.create_volume_backup, 'volume1', 'volume1-backup5'],
		[TestAction.detach_volume, 'volume1'],
		[TestAction.resize_volume, 'vm2', 5*1024*1024],
		[TestAction.delete_image, 'image3'],
		[TestAction.recover_image, 'image3'],
		[TestAction.attach_volume, 'vm1', 'volume1'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.use_volume_backup, 'volume1-backup1'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.detach_volume, 'volume1'],
		[TestAction.add_image, 'image4', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.create_volume, 'volume3', 'flag=scsi'],
		[TestAction.attach_volume, 'vm4', 'volume1'],
])



'''
Running:['vm3', 'vm2', 'vm4', 'vm5', 'vm1']
Stopped:[]
Enadbled:['volume1-backup1', 'vm2-backup2', 'volume1-backup2', 'volume1-backup4', 'volume1-backup5', 'vm2-image1', 'image3', 'image4']
attached:['volume1']
Detached:['volume3']
Deleted:['volume2']
Expunged:['image2']
Ha:[]
Group:
	vm_backup1:['vm2-backup2', 'volume1-backup2']---vm2_volume1
'''
