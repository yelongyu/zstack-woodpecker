import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", path_list=[
		[TestAction.add_image, 'image1', 'root', os.environ.get('isoForVmUrl')],
		[TestAction.create_vm_by_image, 'image1', 'iso', 'vm1'],
		[TestAction.create_volume, 'volume1', 'flag=scsi'],
		[TestAction.attach_volume, 'vm1', 'volume1'],
		[TestAction.create_volume_backup, 'volume1', 'volume1-backup1'],
		[TestAction.detach_volume, 'volume1'],
		[TestAction.create_mini_vm, 'vm2', 'flag=thick'],
		[TestAction.resize_volume, 'vm1', 5*1024*1024],
		[TestAction.create_volume, 'volume2', 'size=random', 'flag=scsi'],
		[TestAction.create_mini_vm, 'vm3', 'network=random'],
		[TestAction.create_volume, 'volume3', 'flag=thick,scsi'],
		[TestAction.add_image, 'image2', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.create_vm_backup, 'vm1', 'vm1-backup2'],
		[TestAction.delete_vm_backup, 'vm1-backup2'],
		[TestAction.delete_image, 'image1'],
		[TestAction.delete_image, 'image2'],
		[TestAction.expunge_image, 'image2'],
		[TestAction.create_vm_backup, 'vm1', 'vm1-backup3'],
		[TestAction.recover_image, 'image1'],
		[TestAction.create_vm_by_image, 'image1', 'iso', 'vm4'],
		[TestAction.delete_image, 'image1'],
		[TestAction.migrate_vm, 'vm3'],
		[TestAction.create_volume, 'volume4', 'flag=scsi'],
		[TestAction.attach_volume, 'vm1', 'volume4'],
		[TestAction.create_volume, 'volume5', 'flag=thin,scsi'],
		[TestAction.stop_vm, 'vm4'],
		[TestAction.start_vm, 'vm4'],
		[TestAction.add_image, 'image3', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.delete_volume, 'volume1'],
		[TestAction.expunge_volume, 'volume1'],
		[TestAction.create_mini_vm, 'vm5', ],
		[TestAction.create_vm_backup, 'vm4', 'vm4-backup4'],
		[TestAction.resize_volume, 'vm2', 5*1024*1024],
		[TestAction.recover_image, 'image1'],
		[TestAction.attach_volume, 'vm2', 'volume2'],
		[TestAction.create_volume_backup, 'volume2', 'volume2-backup5'],
		[TestAction.delete_volume_backup, 'volume2-backup5'],
		[TestAction.detach_volume, 'volume2'],
		[TestAction.add_image, 'image4', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.attach_volume, 'vm3', 'volume3'],
])



'''
The final status:
Running:['vm1', 'vm2', 'vm3', 'vm4', 'vm5']
Stopped:[]
Enadbled:['volume1-backup1', 'vm1-backup3', 'vm4-backup4', 'image3', 'image1', 'image4']
attached:['volume4', 'volume3']
Detached:['volume5', 'volume2']
Deleted:['vm1-backup2', 'volume2-backup5']
Expunged:['volume1', 'image2']
Ha:[]
Group:
	vm_backup2:['vm4-backup4']---vm4_
	vm_backup1:['vm1-backup3']---vm1_
'''
