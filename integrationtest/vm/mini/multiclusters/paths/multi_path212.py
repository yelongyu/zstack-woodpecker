import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", checking_point=1, faild_point=100000, path_list=[
		[TestAction.create_mini_vm, 'vm1', 'cluster=cluster2'],
		[TestAction.change_vm_ha, 'vm1'],
		[TestAction.create_mini_vm, 'vm2', 'cluster=cluster1'],
		[TestAction.create_volume, 'volume1', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.attach_volume, 'vm2', 'volume1'],
		[TestAction.create_volume_backup, 'volume1', 'volume1-backup1'],
		[TestAction.create_mini_vm, 'vm3', 'cluster=cluster2', 'flag=thin'],
		[TestAction.resize_volume, 'vm1', 5*1024*1024],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.create_volume, 'volume2', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.attach_volume, 'vm3', 'volume2'],
		[TestAction.create_volume, 'volume3', 'cluster=cluster1', 'flag=thin,scsi'],
		[TestAction.add_image, 'image1', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.create_volume, 'volume4', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.attach_volume, 'vm1', 'volume4'],
		[TestAction.create_volume_backup, 'volume4', 'volume4-backup2'],
		[TestAction.delete_volume_backup, 'volume4-backup2'],
		[TestAction.delete_image, 'image1'],
		[TestAction.recover_image, 'image1'],
		[TestAction.delete_image, 'image1'],
		[TestAction.expunge_image, 'image1'],
		[TestAction.create_vm_backup, 'vm1', 'vm1-backup3'],
		[TestAction.create_mini_vm, 'vm4', 'cluster=cluster1'],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.resize_data_volume, 'volume3', 5*1024*1024],
		[TestAction.detach_volume, 'volume1'],
		[TestAction.delete_volume, 'volume3'],
		[TestAction.recover_volume, 'volume3'],
		[TestAction.delete_vm_backup, 'vm1-backup3'],
		[TestAction.change_vm_ha, 'vm1'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.delete_volume, 'volume4'],
		[TestAction.expunge_volume, 'volume4'],
		[TestAction.create_mini_vm, 'vm5', 'data_volume=true', 'cluster=cluster1'],
		[TestAction.attach_volume, 'vm5', 'volume1'],
		[TestAction.create_volume_backup, 'volume1', 'volume1-backup5'],
		[TestAction.create_image_from_volume, 'vm2', 'vm2-image2'],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.delete_volume_backup, 'volume1-backup5'],
])




'''
The final status:
Running:['vm5']
Stopped:['vm2', 'vm4', 'vm1', 'vm3']
Enadbled:['volume1-backup1', 'vm2-image2']
attached:['volume2', 'auto-volume5', 'volume1']
Detached:['volume3']
Deleted:['volume4-backup2', 'vm1-backup3', 'volume4-backup3', 'volume1-backup5']
Expunged:['volume4', 'image1']
Ha:[]
Group:
'''