import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", checking_point=1, faild_point=100000, path_list=[
		[TestAction.create_mini_vm, 'vm1', 'cluster=cluster1'],
		[TestAction.destroy_vm, 'vm1'],
		[TestAction.recover_vm, 'vm1'],
		[TestAction.create_mini_vm, 'vm2', 'cluster=cluster2'],
		[TestAction.create_vm_backup, 'vm2', 'vm2-backup1'],
		[TestAction.create_mini_vm, 'vm3', 'memory=random', 'cluster=cluster1'],
		[TestAction.create_volume, 'volume1', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.resize_data_volume, 'volume1', 5*1024*1024],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.attach_volume, 'vm1', 'volume1'],
		[TestAction.detach_volume, 'volume1'],
		[TestAction.create_volume, 'volume2', 'cluster=cluster1', 'flag=thick,scsi'],
		[TestAction.add_image, 'image1', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.attach_volume, 'vm3', 'volume1'],
		[TestAction.start_vm, 'vm3'],
		[TestAction.create_volume_backup, 'volume1', 'volume1-backup2'],
		[TestAction.stop_vm, 'vm3'],
		[TestAction.delete_volume_backup, 'volume1-backup2'],
		[TestAction.delete_image, 'image1'],
		[TestAction.expunge_image, 'image1'],
		[TestAction.create_volume, 'volume3', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.attach_volume, 'vm2', 'volume3'],
		[TestAction.create_volume_backup, 'volume3', 'volume3-backup3'],
		[TestAction.destroy_vm, 'vm1'],
		[TestAction.recover_vm, 'vm1'],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.resize_data_volume, 'volume3', 5*1024*1024],
		[TestAction.create_volume, 'volume4', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.attach_volume, 'vm2', 'volume4'],
		[TestAction.delete_volume, 'volume3'],
		[TestAction.delete_vm_backup, 'vm2-backup1'],
		[TestAction.create_mini_vm, 'vm4', 'cpu=random', 'cluster=cluster2'],
		[TestAction.delete_volume, 'volume2'],
		[TestAction.expunge_volume, 'volume2'],
		[TestAction.start_vm, 'vm2'],
		[TestAction.reboot_vm, 'vm2'],
		[TestAction.create_vm_backup, 'vm2', 'vm2-backup4'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.migrate_vm, 'vm1'],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.recover_volume, 'volume3'],
		[TestAction.use_volume_backup, 'volume3-backup3'],
])




'''
The final status:
Running:['vm1']
Stopped:['vm3', 'vm4', 'vm2']
Enadbled:['volume3-backup3', 'vm2-backup4', 'volume4-backup4']
attached:['volume1', 'volume4']
Detached:['volume3']
Deleted:['volume1-backup2', 'vm2-backup1']
Expunged:['volume2', 'image1']
Ha:[]
Group:
	vm_backup1:['vm2-backup4', 'volume4-backup4']---vm2@volume4
'''