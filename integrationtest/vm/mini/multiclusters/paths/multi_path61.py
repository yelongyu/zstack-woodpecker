import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", checking_point=1, faild_point=100000, path_list=[
		[TestAction.create_mini_vm, 'vm1', 'data_volume=true', 'cluster=cluster2'],
		[TestAction.create_mini_vm, 'vm2', 'cluster=cluster1'],
		[TestAction.create_volume, 'volume2', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.attach_volume, 'vm2', 'volume2'],
		[TestAction.create_volume_backup, 'volume2', 'volume2-backup1'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.resize_volume, 'vm2', 5*1024*1024],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.create_volume, 'volume3', 'size=random', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.create_volume, 'volume4', 'cluster=cluster1', 'flag=thick,scsi'],
		[TestAction.add_image, 'image1', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.create_vm_backup, 'vm1', 'vm1-backup2'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.use_vm_backup, 'vm1-backup2'],
		[TestAction.delete_image, 'image1'],
		[TestAction.expunge_image, 'image1'],
		[TestAction.attach_volume, 'vm2', 'volume4'],
		[TestAction.create_volume_backup, 'volume4', 'volume4-backup4'],
		[TestAction.reboot_vm, 'vm2'],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.create_image_from_volume, 'vm2', 'vm2-image2'],
		[TestAction.create_volume, 'volume5', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.attach_volume, 'vm2', 'volume5'],
		[TestAction.create_volume, 'volume6', 'cluster=cluster1', 'flag=thick,scsi'],
		[TestAction.delete_volume_backup, 'volume2-backup1'],
		[TestAction.create_mini_vm, 'vm3', 'memory=random', 'cluster=cluster2'],
		[TestAction.delete_volume, 'volume3'],
		[TestAction.expunge_volume, 'volume3'],
		[TestAction.change_vm_ha, 'vm2'],
		[TestAction.attach_volume, 'vm2', 'volume6'],
		[TestAction.create_volume_backup, 'volume6', 'volume6-backup5'],
		[TestAction.create_volume, 'volume7', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.resize_data_volume, 'volume7', 5*1024*1024],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.create_volume, 'volume8', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.attach_volume, 'vm2', 'volume8'],
		[TestAction.create_volume_backup, 'volume8', 'volume8-backup6'],
		[TestAction.delete_volume_backup, 'volume8-backup6'],
])




'''
The final status:
Running:['vm2']
Stopped:['vm1', 'vm3']
Enadbled:['vm1-backup2', 'auto-volume1-backup2', 'volume4-backup4', 'volume6-backup5', 'vm2-image2']
attached:['auto-volume1', 'volume2', 'volume4', 'volume5', 'volume6', 'volume8']
Detached:['volume7']
Deleted:['volume2-backup1', 'volume8-backup6']
Expunged:['volume3', 'image1']
Ha:['vm2']
Group:
	vm_backup1:['vm1-backup2', 'auto-volume1-backup2']---vm1@auto-volume1
'''