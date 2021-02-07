import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", checking_point=1, faild_point=100000, path_list=[
		[TestAction.create_mini_vm, 'vm1', 'cluster=cluster2'],
		[TestAction.create_volume, 'volume1', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.attach_volume, 'vm1', 'volume1'],
		[TestAction.create_volume_backup, 'volume1', 'volume1-backup1'],
		[TestAction.create_mini_vm, 'vm2', 'cpu=random', 'cluster=cluster1'],
		[TestAction.create_image_from_volume, 'vm2', 'vm2-image1'],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.create_volume, 'volume2', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.attach_volume, 'vm1', 'volume2'],
		[TestAction.create_volume, 'volume3', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.delete_volume, 'volume3'],
		[TestAction.add_image, 'image2', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.create_volume, 'volume4', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.attach_volume, 'vm2', 'volume4'],
		[TestAction.start_vm, 'vm2'],
		[TestAction.create_volume_backup, 'volume4', 'volume4-backup2'],
		[TestAction.stop_vm, 'vm2'],
		[TestAction.delete_volume_backup, 'volume4-backup2'],
		[TestAction.delete_image, 'vm2-image1'],
		[TestAction.expunge_image, 'vm2-image1'],
		[TestAction.start_vm, 'vm2'],
		[TestAction.create_vm_backup, 'vm2', 'vm2-backup3'],
		[TestAction.stop_vm, 'vm2'],
		[TestAction.start_vm, 'vm2'],
		[TestAction.reboot_vm, 'vm2'],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.resize_volume, 'vm1', 5*1024*1024],
		[TestAction.create_volume, 'volume5', 'size=random', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.create_volume, 'volume6', 'cluster=cluster2', 'flag=thick,scsi'],
		[TestAction.delete_vm_backup, 'vm2-backup3'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.expunge_volume, 'volume3'],
		[TestAction.create_mini_vm, 'vm3', 'data_volume=true', 'cluster=cluster2'],
		[TestAction.attach_volume, 'vm3', 'volume6'],
		[TestAction.create_volume_backup, 'volume6', 'volume6-backup5'],
		[TestAction.resize_data_volume, 'volume2', 5*1024*1024],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.delete_volume_backup, 'volume6-backup5'],
])




'''
The final status:
Running:[]
Stopped:['vm2', 'vm1', 'vm3']
Enadbled:['volume1-backup1', 'image2']
attached:['volume1', 'volume2', 'volume4', 'auto-volume3', 'volume6']
Detached:['volume5']
Deleted:['volume4-backup2', 'vm2-backup3', 'volume4-backup3', 'volume6-backup5']
Expunged:['volume3', 'vm2-image1']
Ha:[]
Group:
'''