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
		[TestAction.create_mini_vm, 'vm3', 'cluster=cluster1'],
		[TestAction.create_volume, 'volume4', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.attach_volume, 'vm3', 'volume4'],
		[TestAction.create_volume_backup, 'volume4', 'volume4-backup3'],
		[TestAction.delete_volume_backup, 'volume4-backup3'],
		[TestAction.delete_image, 'image1'],
		[TestAction.expunge_image, 'image1'],
		[TestAction.create_volume, 'volume5', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.attach_volume, 'vm3', 'volume5'],
		[TestAction.create_volume_backup, 'volume5', 'volume5-backup4'],
		[TestAction.create_mini_vm, 'vm4', 'cluster=cluster2'],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.resize_volume, 'vm1', 5*1024*1024],
		[TestAction.create_volume, 'volume6', 'size=random', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.create_volume, 'volume7', 'cluster=cluster1', 'flag=thin,scsi'],
		[TestAction.use_vm_backup, 'vm1-backup1'],
		[TestAction.destroy_vm, 'vm1'],
		[TestAction.expunge_vm, 'vm1'],
		[TestAction.delete_volume, 'volume6'],
		[TestAction.expunge_volume, 'volume6'],
		[TestAction.change_vm_ha, 'vm4'],
		[TestAction.attach_volume, 'vm3', 'volume7'],
		[TestAction.create_volume_backup, 'volume7', 'volume7-backup5'],
		[TestAction.migrate_vm, 'vm4'],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.create_volume, 'volume8', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.attach_volume, 'vm3', 'volume8'],
		[TestAction.create_volume_backup, 'volume8', 'volume8-backup6'],
		[TestAction.stop_vm, 'vm3'],
		[TestAction.use_volume_backup, 'volume8-backup6'],
		[TestAction.start_vm, 'vm3'],
])




'''
The final status:
Running:['vm4', 'vm3']
Stopped:[]
Enadbled:['vm1-backup1', 'auto-volume1-backup1', 'volume5-backup4', 'volume7-backup5', 'volume8-backup6']
attached:['volume4', 'volume5', 'volume7', 'volume8']
Detached:['volume3', 'auto-volume1']
Deleted:['volume2', 'volume4-backup3']
Expunged:['vm2', 'vm1', 'volume6', 'image1']
Ha:['vm4']
Group:
	vm_backup1:['vm1-backup1', 'auto-volume1-backup1']---vm1@auto-volume1
'''