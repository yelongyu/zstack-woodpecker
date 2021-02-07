import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", checking_point=1, faild_point=100000, path_list=[
		[TestAction.create_mini_vm, 'vm1', 'cluster=cluster1'],
		[TestAction.reboot_vm, 'vm1'],
		[TestAction.create_mini_vm, 'vm2', 'cluster=cluster2'],
		[TestAction.create_volume, 'volume1', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.attach_volume, 'vm2', 'volume1'],
		[TestAction.create_volume_backup, 'volume1', 'volume1-backup1'],
		[TestAction.create_mini_vm, 'vm3', 'cluster=cluster2', 'flag=thick'],
		[TestAction.migrate_vm, 'vm1'],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.create_volume, 'volume2', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.attach_volume, 'vm3', 'volume2'],
		[TestAction.create_volume, 'volume3', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.delete_volume, 'volume3'],
		[TestAction.recover_volume, 'volume3'],
		[TestAction.add_image, 'image1', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.create_vm_backup, 'vm1', 'vm1-backup2'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.use_vm_backup, 'vm1-backup2'],
		[TestAction.delete_image, 'image1'],
		[TestAction.recover_image, 'image1'],
		[TestAction.delete_image, 'image1'],
		[TestAction.expunge_image, 'image1'],
		[TestAction.create_vm_backup, 'vm2', 'vm2-backup3'],
		[TestAction.destroy_vm, 'vm3'],
		[TestAction.recover_vm, 'vm3'],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.migrate_vm, 'vm1'],
		[TestAction.attach_volume, 'vm1', 'volume3'],
		[TestAction.create_volume, 'volume4', 'cluster=cluster2', 'flag=thick,scsi'],
		[TestAction.attach_volume, 'vm2', 'volume2'],
		[TestAction.create_volume_backup, 'volume2', 'volume2-backup5'],
		[TestAction.delete_volume_backup, 'volume2-backup5'],
		[TestAction.create_mini_vm, 'vm4', 'memory=random', 'cluster=cluster2'],
		[TestAction.delete_volume, 'volume1'],
		[TestAction.expunge_volume, 'volume1'],
		[TestAction.destroy_vm, 'vm4'],
		[TestAction.recover_vm, 'vm4'],
		[TestAction.create_vm_backup, 'vm1', 'vm1-backup6'],
		[TestAction.resize_volume, 'vm1', 5*1024*1024],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.delete_vm_backup, 'vm1-backup2'],
])




'''
The final status:
Running:['vm2']
Stopped:['vm3', 'vm4', 'vm1']
Enadbled:['volume1-backup1', 'vm2-backup3', 'volume1-backup3', 'vm1-backup6', 'volume3-backup6']
attached:['volume3', 'volume2']
Detached:['volume4']
Deleted:['volume2-backup5', 'vm1-backup2']
Expunged:['volume1', 'image1']
Ha:[]
Group:
	vm_backup2:['vm2-backup3', 'volume1-backup3']---vm2@volume1
	vm_backup3:['vm1-backup6', 'volume3-backup6']---vm1@volume3
'''