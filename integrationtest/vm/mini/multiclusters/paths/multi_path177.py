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
		[TestAction.create_mini_vm, 'vm2', 'cluster=cluster1'],
		[TestAction.start_vm, 'vm2'],
		[TestAction.resize_volume, 'vm1', 5*1024*1024],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.create_volume, 'volume2', 'size=random', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.create_volume, 'volume3', 'cluster=cluster2', 'flag=thin,scsi'],
		[TestAction.add_image, 'image1', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.delete_volume_backup, 'volume1-backup1'],
		[TestAction.delete_image, 'image1'],
		[TestAction.expunge_image, 'image1'],
		[TestAction.create_vm_backup, 'vm2', 'vm2-backup2'],
		[TestAction.reboot_vm, 'vm1'],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.create_image_from_volume, 'vm1', 'vm1-image2'],
		[TestAction.attach_volume, 'vm1', 'volume3'],
		[TestAction.detach_volume, 'volume3'],
		[TestAction.delete_volume, 'volume2'],
		[TestAction.attach_volume, 'vm2', 'volume3'],
		[TestAction.create_volume_backup, 'volume3', 'volume3-backup3'],
		[TestAction.stop_vm, 'vm2'],
		[TestAction.use_volume_backup, 'volume3-backup3'],
		[TestAction.start_vm, 'vm2'],
		[TestAction.detach_volume, 'volume3'],
		[TestAction.create_mini_vm, 'vm3', 'cpu=random', 'cluster=cluster2'],
		[TestAction.expunge_volume, 'volume2'],
		[TestAction.destroy_vm, 'vm3'],
		[TestAction.attach_volume, 'vm2', 'volume3'],
		[TestAction.create_volume_backup, 'volume3', 'volume3-backup4'],
		[TestAction.detach_volume, 'volume3'],
		[TestAction.resize_volume, 'vm2', 5*1024*1024],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.delete_vm_backup, 'vm2-backup2'],
])




'''
The final status:
Running:['vm1', 'vm2']
Stopped:[]
Enadbled:['volume3-backup3', 'volume3-backup4', 'vm1-image2']
attached:[]
Detached:['volume1', 'volume3']
Deleted:['vm3', 'volume1-backup1', 'vm2-backup2']
Expunged:['volume2', 'image1']
Ha:[]
Group:
'''