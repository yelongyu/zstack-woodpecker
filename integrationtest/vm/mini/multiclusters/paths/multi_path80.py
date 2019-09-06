import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", checking_point=1, faild_point=100000, path_list=[
		[TestAction.create_mini_vm, 'vm1', 'cluster=cluster1'],
		[TestAction.reboot_vm, 'vm1'],
		[TestAction.create_mini_vm, 'vm2', 'cluster=cluster2'],
		[TestAction.create_vm_backup, 'vm2', 'vm2-backup1'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.resize_volume, 'vm2', 5*1024*1024],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.create_volume, 'volume1', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.attach_volume, 'vm2', 'volume1'],
		[TestAction.detach_volume, 'volume1'],
		[TestAction.delete_volume, 'volume1'],
		[TestAction.recover_volume, 'volume1'],
		[TestAction.add_image, 'image1', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.attach_volume, 'vm1', 'volume1'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.create_volume_backup, 'volume1', 'volume1-backup2'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.use_volume_backup, 'volume1-backup2'],
		[TestAction.detach_volume, 'volume1'],
		[TestAction.delete_image, 'image1'],
		[TestAction.expunge_image, 'image1'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.create_vm_backup, 'vm1', 'vm1-backup3'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.reboot_vm, 'vm1'],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.resize_volume, 'vm2', 5*1024*1024],
		[TestAction.create_volume, 'volume2', 'size=random', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.create_volume, 'volume3', 'cluster=cluster2', 'flag=thin,scsi'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.use_vm_backup, 'vm1-backup3'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.destroy_vm, 'vm2'],
		[TestAction.expunge_vm, 'vm2'],
		[TestAction.delete_volume, 'volume2'],
		[TestAction.expunge_volume, 'volume2'],
		[TestAction.create_mini_vm, 'vm3', 'cluster=cluster2'],
		[TestAction.destroy_vm, 'vm3'],
		[TestAction.create_vm_backup, 'vm1', 'vm1-backup4'],
		[TestAction.migrate_vm, 'vm1'],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.delete_volume_backup, 'volume1-backup2'],
])




'''
The final status:
Running:['vm1']
Stopped:[]
Enadbled:['vm2-backup1', 'vm1-backup3', 'vm1-backup4']
attached:[]
Detached:['volume1', 'volume3']
Deleted:['vm3', 'volume1-backup2']
Expunged:['vm2', 'volume2', 'image1']
Ha:[]
Group:
	vm_backup2:['vm1-backup3']---vm1@
	vm_backup3:['vm1-backup4']---vm1@
	vm_backup1:['vm2-backup1']---vm2@
'''