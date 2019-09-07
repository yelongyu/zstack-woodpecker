import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", checking_point=1, faild_point=100000, path_list=[
		[TestAction.create_mini_vm, 'vm1', 'cluster=cluster1'],
		[TestAction.change_vm_ha, 'vm1'],
		[TestAction.create_vm_backup, 'vm1', 'vm1-backup1'],
		[TestAction.create_mini_vm, 'vm2', 'memory=random', 'cluster=cluster1'],
		[TestAction.resize_volume, 'vm2', 5*1024*1024],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.create_volume, 'volume1', 'size=random', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.delete_volume, 'volume1'],
		[TestAction.recover_volume, 'volume1'],
		[TestAction.add_image, 'image1', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.delete_vm_backup, 'vm1-backup1'],
		[TestAction.delete_image, 'image1'],
		[TestAction.expunge_image, 'image1'],
		[TestAction.attach_volume, 'vm1', 'volume1'],
		[TestAction.create_volume_backup, 'volume1', 'volume1-backup2'],
		[TestAction.detach_volume, 'volume1'],
		[TestAction.create_mini_vm, 'vm3', 'data_volume=true', 'cluster=cluster1'],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.resize_data_volume, 'volume1', 5*1024*1024],
		[TestAction.create_volume, 'volume3', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.attach_volume, 'vm2', 'volume3'],
		[TestAction.delete_volume, 'volume1'],
		[TestAction.recover_volume, 'volume1'],
		[TestAction.start_vm, 'vm2'],
		[TestAction.create_vm_backup, 'vm2', 'vm2-backup3'],
		[TestAction.stop_vm, 'vm2'],
		[TestAction.use_vm_backup, 'vm2-backup3'],
		[TestAction.create_mini_vm, 'vm4', 'cluster=cluster1', 'flag=thin'],
		[TestAction.delete_volume, 'volume1'],
		[TestAction.expunge_volume, 'volume1'],
		[TestAction.create_mini_vm, 'vm5', 'cluster=cluster2'],
		[TestAction.create_vm_backup, 'vm5', 'vm5-backup5'],
		[TestAction.resize_volume, 'vm3', 5*1024*1024],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.use_vm_backup, 'vm5-backup5'],
])




'''
The final status:
Running:['vm1', 'vm3', 'vm4']
Stopped:['vm5', 'vm2']
Enadbled:['volume1-backup2', 'vm2-backup3', 'volume3-backup3', 'vm5-backup5']
attached:['auto-volume3', 'volume3']
Detached:[]
Deleted:['vm1-backup1']
Expunged:['volume1', 'image1']
Ha:['vm1']
Group:
	vm_backup2:['vm5-backup5']---vm5@
	vm_backup1:['vm2-backup3', 'volume3-backup3']---vm2@volume3
'''