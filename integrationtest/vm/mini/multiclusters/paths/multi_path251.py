import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", checking_point=1, faild_point=100000, path_list=[
		[TestAction.create_mini_vm, 'vm1', 'cluster=cluster1'],
		[TestAction.change_vm_ha, 'vm1'],
		[TestAction.create_vm_backup, 'vm1', 'vm1-backup1'],
		[TestAction.create_mini_vm, 'vm2', 'cluster=cluster2'],
		[TestAction.destroy_vm, 'vm2'],
		[TestAction.expunge_vm, 'vm2'],
		[TestAction.resize_volume, 'vm1', 5*1024*1024],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.create_volume, 'volume1', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.attach_volume, 'vm1', 'volume1'],
		[TestAction.detach_volume, 'volume1'],
		[TestAction.delete_volume, 'volume1'],
		[TestAction.recover_volume, 'volume1'],
		[TestAction.add_image, 'image1', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.delete_vm_backup, 'vm1-backup1'],
		[TestAction.delete_image, 'image1'],
		[TestAction.expunge_image, 'image1'],
		[TestAction.create_vm_backup, 'vm1', 'vm1-backup2'],
		[TestAction.create_mini_vm, 'vm3', 'cluster=cluster2'],
		[TestAction.destroy_vm, 'vm3'],
		[TestAction.recover_vm, 'vm3'],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.create_volume, 'volume2', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.resize_data_volume, 'volume2', 5*1024*1024],
		[TestAction.create_volume, 'volume3', 'size=random', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.delete_volume, 'volume2'],
		[TestAction.attach_volume, 'vm1', 'volume1'],
		[TestAction.create_volume_backup, 'volume1', 'volume1-backup3'],
		[TestAction.delete_volume_backup, 'volume1-backup3'],
		[TestAction.detach_volume, 'volume1'],
		[TestAction.start_vm, 'vm3'],
		[TestAction.delete_volume, 'volume1'],
		[TestAction.expunge_volume, 'volume1'],
		[TestAction.create_mini_vm, 'vm4', 'data_volume=true', 'cluster=cluster2'],
		[TestAction.create_volume_backup, 'auto-volume4', 'auto-volume4-backup4'],
		[TestAction.resize_volume, 'vm1', 5*1024*1024],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.create_vm_backup, 'vm4', 'vm4-backup5'],
		[TestAction.stop_vm, 'vm4'],
		[TestAction.use_vm_backup, 'vm4-backup5'],
		[TestAction.start_vm, 'vm4'],
])




'''
The final status:
Running:['vm1', 'vm3', 'vm4']
Stopped:[]
Enadbled:['vm1-backup2', 'auto-volume4-backup4', 'vm4-backup5', 'auto-volume4-backup5']
attached:['auto-volume4']
Detached:['volume3']
Deleted:['volume2', 'vm1-backup1', 'volume1-backup3']
Expunged:['vm2', 'volume1', 'image1']
Ha:['vm1']
Group:
	vm_backup2:['vm4-backup5', 'auto-volume4-backup5']---vm4@auto-volume4
	vm_backup1:['vm1-backup2']---vm1@
'''