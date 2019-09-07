import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", checking_point=1, faild_point=100000, path_list=[
		[TestAction.create_mini_vm, 'vm1', 'data_volume=true', 'cluster=cluster1'],
		[TestAction.create_volume_backup, 'auto-volume1', 'auto-volume1-backup1'],
		[TestAction.create_mini_vm, 'vm2', 'cluster=cluster1'],
		[TestAction.stop_vm, 'vm2'],
		[TestAction.start_vm, 'vm2'],
		[TestAction.create_volume, 'volume2', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.resize_data_volume, 'volume2', 5*1024*1024],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.attach_volume, 'vm2', 'volume2'],
		[TestAction.detach_volume, 'volume2'],
		[TestAction.create_volume, 'volume3', 'cluster=cluster1', 'flag=thin,scsi'],
		[TestAction.add_image, 'image1', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.start_vm, 'vm2'],
		[TestAction.create_vm_backup, 'vm2', 'vm2-backup2'],
		[TestAction.delete_vm_backup, 'vm2-backup2'],
		[TestAction.stop_vm, 'vm2'],
		[TestAction.delete_image, 'image1'],
		[TestAction.expunge_image, 'image1'],
		[TestAction.attach_volume, 'vm1', 'volume2'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.create_volume_backup, 'volume2', 'volume2-backup3'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.detach_volume, 'volume2'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.reboot_vm, 'vm1'],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.resize_data_volume, 'volume2', 5*1024*1024],
		[TestAction.create_mini_vm, 'vm3', 'cluster=cluster2'],
		[TestAction.create_volume, 'volume4', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.attach_volume, 'vm3', 'volume4'],
		[TestAction.create_volume, 'volume5', 'cluster=cluster1', 'flag=thin,scsi'],
		[TestAction.use_volume_backup, 'auto-volume1-backup1'],
		[TestAction.create_mini_vm, 'vm4', 'cluster=cluster1', 'flag=thick'],
		[TestAction.delete_volume, 'volume5'],
		[TestAction.expunge_volume, 'volume5'],
		[TestAction.create_mini_vm, 'vm5', 'cluster=cluster2'],
		[TestAction.create_volume_backup, 'volume4', 'volume4-backup4'],
		[TestAction.create_image_from_volume, 'vm4', 'vm4-image2'],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.create_vm_backup, 'vm1', 'vm1-backup5'],
		[TestAction.delete_vm_backup, 'vm1-backup5'],
		[TestAction.stop_vm, 'vm1'],
])




'''
The final status:
Running:['vm4']
Stopped:['vm2', 'vm3', 'vm5', 'vm1']
Enadbled:['auto-volume1-backup1', 'volume2-backup3', 'volume4-backup4', 'vm4-image2']
attached:['auto-volume1', 'volume4']
Detached:['volume3', 'volume2']
Deleted:['vm2-backup2', 'vm1-backup5', 'auto-volume1-backup5']
Expunged:['volume5', 'image1']
Ha:[]
Group:
'''