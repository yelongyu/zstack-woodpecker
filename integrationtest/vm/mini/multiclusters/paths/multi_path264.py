import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", checking_point=1, faild_point=100000, path_list=[
		[TestAction.create_mini_vm, 'vm1', 'cluster=cluster2'],
		[TestAction.create_volume, 'volume1', 'flag=scsi'],
		[TestAction.attach_volume, 'vm1', 'volume1'],
		[TestAction.create_volume_backup, 'volume1', 'volume1-backup1'],
		[TestAction.detach_volume, 'volume1'],
		[TestAction.create_mini_vm, 'vm2', 'cpu=random', 'cluster=cluster1'],
		[TestAction.create_volume, 'volume2', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.resize_data_volume, 'volume2', 5*1024*1024],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.create_volume, 'volume3', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.attach_volume, 'vm1', 'volume3'],
		[TestAction.create_volume, 'volume4', 'cluster=cluster2', 'flag=thick,scsi'],
		[TestAction.add_image, 'image1', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.create_vm_backup, 'vm1', 'vm1-backup2'],
		[TestAction.delete_vm_backup, 'vm1-backup2'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.delete_image, 'image1'],
		[TestAction.expunge_image, 'image1'],
		[TestAction.attach_volume, 'vm1', 'volume1'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.create_volume_backup, 'volume1', 'volume1-backup4'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.detach_volume, 'volume1'],
		[TestAction.create_mini_vm, 'vm3', 'cluster=cluster1'],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.migrate_vm, 'vm1'],
		[TestAction.attach_volume, 'vm2', 'volume2'],
		[TestAction.create_volume, 'volume5', 'cluster=cluster1', 'flag=thick,scsi'],
		[TestAction.attach_volume, 'vm1', 'volume1'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.use_volume_backup, 'volume1-backup1'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.detach_volume, 'volume1'],
		[TestAction.create_mini_vm, 'vm4', 'cluster=cluster1', 'flag=thin'],
		[TestAction.delete_volume, 'volume4'],
		[TestAction.expunge_volume, 'volume4'],
		[TestAction.reboot_vm, 'vm1'],
		[TestAction.attach_volume, 'vm2', 'volume1'],
		[TestAction.create_volume_backup, 'volume1', 'volume1-backup5'],
		[TestAction.detach_volume, 'volume1'],
		[TestAction.create_image_from_volume, 'vm1', 'vm1-image2'],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.create_vm_backup, 'vm1', 'vm1-backup6'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.use_vm_backup, 'vm1-backup6'],
])




'''
The final status:
Running:['vm2', 'vm3', 'vm4']
Stopped:['vm1']
Enadbled:['volume1-backup1', 'volume1-backup4', 'volume1-backup5', 'vm1-backup6', 'volume3-backup6', 'vm1-image2']
attached:['volume3', 'volume2']
Detached:['volume5', 'volume1']
Deleted:['vm1-backup2', 'volume3-backup2']
Expunged:['volume4', 'image1']
Ha:[]
Group:
	vm_backup1:['vm1-backup6', 'volume3-backup6']---vm1@volume3
'''