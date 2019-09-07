import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", checking_point=1, faild_point=100000, path_list=[
		[TestAction.create_mini_vm, 'vm1', 'cluster=cluster2'],
		[TestAction.create_mini_vm, 'vm2', 'cluster=cluster1'],
		[TestAction.create_vm_backup, 'vm2', 'vm2-backup1'],
		[TestAction.create_mini_vm, 'vm3', 'cluster=cluster2', 'flag=thin'],
		[TestAction.resize_volume, 'vm2', 5*1024*1024],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.create_volume, 'volume1', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.attach_volume, 'vm1', 'volume1'],
		[TestAction.create_volume, 'volume2', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.delete_volume, 'volume2'],
		[TestAction.recover_volume, 'volume2'],
		[TestAction.add_image, 'image1', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.start_vm, 'vm3'],
		[TestAction.create_vm_backup, 'vm3', 'vm3-backup2'],
		[TestAction.stop_vm, 'vm3'],
		[TestAction.use_vm_backup, 'vm3-backup2'],
		[TestAction.delete_image, 'image1'],
		[TestAction.expunge_image, 'image1'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.create_vm_backup, 'vm1', 'vm1-backup3'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.destroy_vm, 'vm2'],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.resize_data_volume, 'volume1', 5*1024*1024],
		[TestAction.create_volume, 'volume3', 'size=random', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.create_volume, 'volume4', 'cluster=cluster1', 'flag=thick,scsi'],
		[TestAction.use_vm_backup, 'vm3-backup2'],
		[TestAction.create_mini_vm, 'vm4', 'cluster=cluster1', 'flag=thick'],
		[TestAction.delete_volume, 'volume4'],
		[TestAction.expunge_volume, 'volume4'],
		[TestAction.change_vm_ha, 'vm3'],
		[TestAction.attach_volume, 'vm3', 'volume2'],
		[TestAction.create_volume_backup, 'volume2', 'volume2-backup5'],
		[TestAction.detach_volume, 'volume2'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.migrate_vm, 'vm1'],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.attach_volume, 'vm1', 'volume2'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.use_volume_backup, 'volume2-backup5'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.detach_volume, 'volume2'],
])




'''
The final status:
Running:['vm3', 'vm1']
Stopped:['vm4']
Enadbled:['vm2-backup1', 'vm3-backup2', 'vm1-backup3', 'volume1-backup3', 'volume2-backup5']
attached:['volume1']
Detached:['volume3', 'volume2']
Deleted:['vm2']
Expunged:['volume4', 'image1']
Ha:['vm3']
Group:
	vm_backup2:['vm3-backup2']---vm3@
	vm_backup3:['vm1-backup3', 'volume1-backup3']---vm1@volume1
	vm_backup1:['vm2-backup1']---vm2@
'''