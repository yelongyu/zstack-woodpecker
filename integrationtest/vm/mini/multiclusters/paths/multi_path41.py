import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", checking_point=1, faild_point=100000, path_list=[
		[TestAction.create_mini_vm, 'vm1', 'cluster=cluster1'],
		[TestAction.destroy_vm, 'vm1'],
		[TestAction.create_volume, 'volume1', 'flag=scsi'],
		[TestAction.create_mini_vm, 'vm2', ],
		[TestAction.attach_volume, 'vm2', 'volume1'],
		[TestAction.create_volume_backup, 'volume1', 'volume1-backup1'],
		[TestAction.detach_volume, 'volume1'],
		[TestAction.create_mini_vm, 'vm3', 'cluster=cluster2'],
		[TestAction.stop_vm, 'vm3'],
		[TestAction.start_vm, 'vm3'],
		[TestAction.create_mini_vm, 'vm4', 'cluster=cluster1'],
		[TestAction.migrate_vm, 'vm4'],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.create_volume, 'volume2', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.attach_volume, 'vm3', 'volume2'],
		[TestAction.create_volume, 'volume3', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.delete_volume, 'volume3'],
		[TestAction.add_image, 'image1', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.start_vm, 'vm4'],
		[TestAction.create_vm_backup, 'vm4', 'vm4-backup2'],
		[TestAction.delete_vm_backup, 'vm4-backup2'],
		[TestAction.stop_vm, 'vm4'],
		[TestAction.delete_image, 'image1'],
		[TestAction.expunge_image, 'image1'],
		[TestAction.create_vm_backup, 'vm3', 'vm3-backup3'],
		[TestAction.change_vm_ha, 'vm3'],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.start_vm, 'vm4'],
		[TestAction.migrate_vm, 'vm4'],
		[TestAction.create_volume, 'volume4', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.attach_volume, 'vm4', 'volume4'],
		[TestAction.delete_volume, 'volume4'],
		[TestAction.recover_volume, 'volume4'],
		[TestAction.attach_volume, 'vm4', 'volume1'],
		[TestAction.stop_vm, 'vm4'],
		[TestAction.use_volume_backup, 'volume1-backup1'],
		[TestAction.start_vm, 'vm4'],
		[TestAction.detach_volume, 'volume1'],
		[TestAction.create_mini_vm, 'vm5', 'cluster=cluster1'],
		[TestAction.stop_vm, 'vm5'],
		[TestAction.start_vm, 'vm5'],
		[TestAction.expunge_volume, 'volume3'],
		[TestAction.create_mini_vm, 'vm6', 'cluster=cluster2'],
		[TestAction.create_volume_backup, 'volume2', 'volume2-backup5'],
		[TestAction.resize_volume, 'vm4', 5*1024*1024],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.attach_volume, 'vm2', 'volume1'],
		[TestAction.stop_vm, 'vm2'],
		[TestAction.use_volume_backup, 'volume1-backup1'],
		[TestAction.start_vm, 'vm2'],
		[TestAction.detach_volume, 'volume1'],
])




'''
The final status:
Running:['vm3', 'vm4', 'vm5', 'vm2']
Stopped:['vm6']
Enadbled:['volume1-backup1', 'vm3-backup3', 'volume2-backup3', 'volume2-backup5']
attached:['volume2']
Detached:['volume4', 'volume1']
Deleted:['vm1', 'vm4-backup2']
Expunged:['volume3', 'image1']
Ha:['vm3']
Group:
	vm_backup1:['vm3-backup3', 'volume2-backup3']---vm3@volume2
'''