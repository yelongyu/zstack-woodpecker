import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", checking_point=1, faild_point=100000, path_list=[
		[TestAction.create_mini_vm, 'vm1', 'data_volume=true', 'cluster=cluster1'],
		[TestAction.create_vm_backup, 'vm1', 'vm1-backup1'],
		[TestAction.create_mini_vm, 'vm2', 'cluster=cluster2'],
		[TestAction.destroy_vm, 'vm2'],
		[TestAction.expunge_vm, 'vm2'],
		[TestAction.migrate_vm, 'vm1'],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.create_volume, 'volume2', 'size=random', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.create_volume, 'volume3', 'cluster=cluster2', 'flag=thick,scsi'],
		[TestAction.add_image, 'image1', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.attach_volume, 'vm1', 'volume3'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.create_volume_backup, 'volume3', 'volume3-backup3'],
		[TestAction.delete_volume_backup, 'volume3-backup3'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.detach_volume, 'volume3'],
		[TestAction.delete_image, 'image1'],
		[TestAction.expunge_image, 'image1'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.create_volume_backup, 'auto-volume1', 'auto-volume1-backup4'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.create_mini_vm, 'vm3', 'cluster=cluster2'],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.resize_volume, 'vm3', 5*1024*1024],
		[TestAction.create_volume, 'volume4', 'size=random', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.delete_volume, 'volume2'],
		[TestAction.use_volume_backup, 'auto-volume1-backup4'],
		[TestAction.create_mini_vm, 'vm4', 'memory=random', 'cluster=cluster2'],
		[TestAction.delete_volume, 'volume4'],
		[TestAction.expunge_volume, 'volume4'],
		[TestAction.reboot_vm, 'vm4'],
		[TestAction.create_vm_backup, 'vm4', 'vm4-backup5'],
		[TestAction.resize_volume, 'vm4', 5*1024*1024],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.use_volume_backup, 'auto-volume1-backup4'],
])




'''
The final status:
Running:['vm4']
Stopped:['vm1', 'vm3']
Enadbled:['vm1-backup1', 'auto-volume1-backup1', 'auto-volume1-backup4', 'vm4-backup5']
attached:['auto-volume1']
Detached:['volume3']
Deleted:['volume2', 'volume3-backup3']
Expunged:['vm2', 'volume4', 'image1']
Ha:[]
Group:
	vm_backup2:['vm4-backup5']---vm4@
	vm_backup1:['vm1-backup1', 'auto-volume1-backup1']---vm1@auto-volume1
'''