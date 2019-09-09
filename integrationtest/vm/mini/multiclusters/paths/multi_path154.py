import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", checking_point=1, faild_point=100000, path_list=[
		[TestAction.create_mini_vm, 'vm1', 'data_volume=true', 'cluster=cluster2'],
		[TestAction.create_vm_backup, 'vm1', 'vm1-backup1'],
		[TestAction.create_mini_vm, 'vm2', 'cluster=cluster1', 'flag=thick'],
		[TestAction.create_volume, 'volume2', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.resize_data_volume, 'volume2', 5*1024*1024],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.attach_volume, 'vm2', 'volume2'],
		[TestAction.create_volume, 'volume3', 'cluster=cluster2', 'flag=thick,scsi'],
		[TestAction.add_image, 'image1', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.delete_vm_backup, 'vm1-backup1'],
		[TestAction.delete_image, 'image1'],
		[TestAction.expunge_image, 'image1'],
		[TestAction.attach_volume, 'vm1', 'volume3'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.create_volume_backup, 'volume3', 'volume3-backup3'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.create_mini_vm, 'vm3', 'cluster=cluster1'],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.migrate_vm, 'vm1'],
		[TestAction.create_volume, 'volume4', 'size=random', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.delete_volume, 'volume2'],
		[TestAction.create_vm_backup, 'vm2', 'vm2-backup4'],
		[TestAction.delete_vm_backup, 'vm2-backup4'],
		[TestAction.create_mini_vm, 'vm4', 'cluster=cluster1', 'flag=thick'],
		[TestAction.expunge_volume, 'volume2'],
		[TestAction.change_vm_ha, 'vm2'],
		[TestAction.create_vm_backup, 'vm1', 'vm1-backup5'],
		[TestAction.resize_volume, 'vm4', 5*1024*1024],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.create_volume, 'volume5', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.attach_volume, 'vm4', 'volume5'],
		[TestAction.start_vm, 'vm4'],
		[TestAction.create_volume_backup, 'volume5', 'volume5-backup8'],
		[TestAction.stop_vm, 'vm4'],
		[TestAction.use_volume_backup, 'volume5-backup8'],
])




'''
The final status:
Running:['vm2', 'vm1']
Stopped:['vm3', 'vm4']
Enadbled:['volume3-backup3', 'vm1-backup5', 'auto-volume1-backup5', 'volume3-backup5', 'volume5-backup8']
attached:['auto-volume1', 'volume3', 'volume5']
Detached:['volume4']
Deleted:['vm1-backup1', 'auto-volume1-backup1', 'vm2-backup4']
Expunged:['volume2', 'image1']
Ha:['vm2']
Group:
	vm_backup1:['vm1-backup5', 'auto-volume1-backup5', 'volume3-backup5']---vm1@auto-volume1_volume3
'''