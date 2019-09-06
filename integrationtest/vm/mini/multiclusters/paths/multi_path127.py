import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", checking_point=1, faild_point=100000, path_list=[
		[TestAction.create_mini_vm, 'vm1', 'cluster=cluster1'],
		[TestAction.reboot_vm, 'vm1'],
		[TestAction.create_vm_backup, 'vm1', 'vm1-backup1'],
		[TestAction.create_mini_vm, 'vm2', 'cluster=cluster2', 'flag=thick'],
		[TestAction.create_image_from_volume, 'vm2', 'vm2-image1'],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.create_volume, 'volume1', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.attach_volume, 'vm2', 'volume1'],
		[TestAction.create_volume, 'volume2', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.delete_volume, 'volume2'],
		[TestAction.add_image, 'image2', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.delete_vm_backup, 'vm1-backup1'],
		[TestAction.delete_image, 'vm2-image1'],
		[TestAction.recover_image, 'vm2-image1'],
		[TestAction.delete_image, 'vm2-image1'],
		[TestAction.expunge_image, 'vm2-image1'],
		[TestAction.create_vm_backup, 'vm2', 'vm2-backup2'],
		[TestAction.destroy_vm, 'vm1'],
		[TestAction.recover_vm, 'vm1'],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.create_volume, 'volume3', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.resize_data_volume, 'volume3', 5*1024*1024],
		[TestAction.create_volume, 'volume4', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.attach_volume, 'vm2', 'volume4'],
		[TestAction.create_volume, 'volume5', 'cluster=cluster1', 'flag=thick,scsi'],
		[TestAction.delete_vm_backup, 'vm2-backup2'],
		[TestAction.create_mini_vm, 'vm3', 'memory=random', 'cluster=cluster1'],
		[TestAction.delete_volume, 'volume5'],
		[TestAction.expunge_volume, 'volume5'],
		[TestAction.create_mini_vm, 'vm4', 'cluster=cluster1'],
		[TestAction.create_volume_backup, 'volume4', 'volume4-backup4'],
		[TestAction.resize_volume, 'vm2', 5*1024*1024],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.create_vm_backup, 'vm3', 'vm3-backup5'],
		[TestAction.delete_vm_backup, 'vm3-backup5'],
])




'''
The final status:
Running:['vm2', 'vm3', 'vm4']
Stopped:['vm1']
Enadbled:['volume4-backup4', 'image2']
attached:['volume1', 'volume4']
Detached:['volume3']
Deleted:['volume2', 'vm1-backup1', 'vm2-backup2', 'volume1-backup2', 'vm3-backup5']
Expunged:['volume5', 'vm2-image1']
Ha:[]
Group:
'''