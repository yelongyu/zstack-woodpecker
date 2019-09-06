import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", checking_point=1, faild_point=100000, path_list=[
		[TestAction.create_mini_vm, 'vm1', 'cluster=cluster2'],
		[TestAction.create_mini_vm, 'vm2', 'cluster=cluster1'],
		[TestAction.create_vm_backup, 'vm2', 'vm2-backup1'],
		[TestAction.create_mini_vm, 'vm3', 'cpu=random', 'cluster=cluster1'],
		[TestAction.resize_volume, 'vm2', 5*1024*1024],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.create_volume, 'volume1', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.attach_volume, 'vm1', 'volume1'],
		[TestAction.detach_volume, 'volume1'],
		[TestAction.create_volume, 'volume2', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.delete_volume, 'volume2'],
		[TestAction.recover_volume, 'volume2'],
		[TestAction.add_image, 'image1', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.attach_volume, 'vm1', 'volume1'],
		[TestAction.create_volume_backup, 'volume1', 'volume1-backup2'],
		[TestAction.delete_volume_backup, 'volume1-backup2'],
		[TestAction.detach_volume, 'volume1'],
		[TestAction.delete_image, 'image1'],
		[TestAction.recover_image, 'image1'],
		[TestAction.delete_image, 'image1'],
		[TestAction.expunge_image, 'image1'],
		[TestAction.create_vm_backup, 'vm1', 'vm1-backup3'],
		[TestAction.destroy_vm, 'vm1'],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.resize_volume, 'vm3', 5*1024*1024],
		[TestAction.create_mini_vm, 'vm4', 'cluster=cluster2'],
		[TestAction.attach_volume, 'vm4', 'volume1'],
		[TestAction.create_volume, 'volume3', 'cluster=cluster1', 'flag=thick,scsi'],
		[TestAction.use_vm_backup, 'vm2-backup1'],
		[TestAction.create_mini_vm, 'vm5', 'network=random', 'cluster=cluster2'],
		[TestAction.delete_volume, 'volume2'],
		[TestAction.expunge_volume, 'volume2'],
		[TestAction.create_mini_vm, 'vm6', 'cluster=cluster2'],
		[TestAction.create_vm_backup, 'vm6', 'vm6-backup4'],
		[TestAction.start_vm, 'vm3'],
		[TestAction.migrate_vm, 'vm3'],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.start_vm, 'vm4'],
		[TestAction.create_volume_backup, 'volume1', 'volume1-backup5'],
		[TestAction.delete_volume_backup, 'volume1-backup5'],
		[TestAction.stop_vm, 'vm4'],
])




'''
The final status:
Running:['vm3']
Stopped:['vm2', 'vm5', 'vm6', 'vm4']
Enadbled:['vm2-backup1', 'vm1-backup3', 'vm6-backup4']
attached:['volume1']
Detached:['volume3']
Deleted:['vm1', 'volume1-backup2', 'volume1-backup5']
Expunged:['volume2', 'image1']
Ha:[]
Group:
	vm_backup2:['vm1-backup3']---vm1@
	vm_backup3:['vm6-backup4']---vm6@
	vm_backup1:['vm2-backup1']---vm2@
'''