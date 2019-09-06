import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", checking_point=1, faild_point=100000, path_list=[
		[TestAction.create_mini_vm, 'vm1', 'data_volume=true', 'cluster=cluster2'],
		[TestAction.create_vm_backup, 'vm1', 'vm1-backup1'],
		[TestAction.create_mini_vm, 'vm2', 'cluster=cluster1'],
		[TestAction.destroy_vm, 'vm2'],
		[TestAction.expunge_vm, 'vm2'],
		[TestAction.create_volume, 'volume2', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.resize_data_volume, 'volume2', 5*1024*1024],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.create_volume, 'volume3', 'size=random', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.delete_volume, 'volume2'],
		[TestAction.add_image, 'image1', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.create_volume_backup, 'auto-volume1', 'auto-volume1-backup3'],
		[TestAction.delete_volume_backup, 'auto-volume1-backup3'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.delete_image, 'image1'],
		[TestAction.expunge_image, 'image1'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.create_volume_backup, 'auto-volume1', 'auto-volume1-backup4'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.create_mini_vm, 'vm3', 'cluster=cluster2'],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.create_mini_vm, 'vm4', 'cluster=cluster1'],
		[TestAction.resize_volume, 'vm4', 5*1024*1024],
		[TestAction.create_volume, 'volume4', 'size=random', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.create_volume, 'volume5', 'cluster=cluster1', 'flag=thin,scsi'],
		[TestAction.use_vm_backup, 'vm1-backup1'],
		[TestAction.destroy_vm, 'vm1'],
		[TestAction.expunge_vm, 'vm1'],
		[TestAction.delete_volume, 'volume4'],
		[TestAction.expunge_volume, 'volume4'],
		[TestAction.change_vm_ha, 'vm3'],
		[TestAction.attach_volume, 'vm4', 'volume3'],
		[TestAction.create_volume_backup, 'volume3', 'volume3-backup5'],
		[TestAction.detach_volume, 'volume3'],
		[TestAction.migrate_vm, 'vm3'],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.attach_volume, 'vm4', 'auto-volume1'],
		[TestAction.stop_vm, 'vm4'],
		[TestAction.use_volume_backup, 'auto-volume1-backup4'],
		[TestAction.start_vm, 'vm4'],
		[TestAction.detach_volume, 'auto-volume1'],
])




'''
The final status:
Running:['vm3', 'vm4']
Stopped:[]
Enadbled:['vm1-backup1', 'auto-volume1-backup1', 'auto-volume1-backup4', 'volume3-backup5']
attached:[]
Detached:['volume5', 'volume3', 'auto-volume1']
Deleted:['volume2', 'auto-volume1-backup3']
Expunged:['vm2', 'vm1', 'volume4', 'image1']
Ha:['vm3']
Group:
	vm_backup1:['vm1-backup1', 'auto-volume1-backup1']---vm1@auto-volume1
'''