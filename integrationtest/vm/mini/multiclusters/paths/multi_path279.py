import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", checking_point=1, faild_point=100000, path_list=[
		[TestAction.create_mini_vm, 'vm1', 'data_volume=true', 'cluster=cluster2'],
		[TestAction.create_mini_vm, 'vm2', 'cluster=cluster1'],
		[TestAction.create_vm_backup, 'vm2', 'vm2-backup1'],
		[TestAction.destroy_vm, 'vm1'],
		[TestAction.expunge_vm, 'vm1'],
		[TestAction.create_mini_vm, 'vm3', 'cluster=cluster2'],
		[TestAction.create_image_from_volume, 'vm3', 'vm3-image1'],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.create_volume, 'volume2', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.attach_volume, 'vm3', 'volume2'],
		[TestAction.create_volume, 'volume3', 'cluster=cluster1', 'flag=thin,scsi'],
		[TestAction.add_image, 'image2', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.start_vm, 'vm3'],
		[TestAction.create_volume_backup, 'volume2', 'volume2-backup2'],
		[TestAction.delete_volume_backup, 'volume2-backup2'],
		[TestAction.stop_vm, 'vm3'],
		[TestAction.delete_image, 'vm3-image1'],
		[TestAction.recover_image, 'vm3-image1'],
		[TestAction.delete_image, 'image2'],
		[TestAction.expunge_image, 'image2'],
		[TestAction.start_vm, 'vm3'],
		[TestAction.create_vm_backup, 'vm3', 'vm3-backup3'],
		[TestAction.stop_vm, 'vm3'],
		[TestAction.create_mini_vm, 'vm4', 'cluster=cluster1'],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.start_vm, 'vm3'],
		[TestAction.migrate_vm, 'vm3'],
		[TestAction.create_volume, 'volume4', 'size=random', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.delete_volume, 'volume4'],
		[TestAction.recover_volume, 'volume4'],
		[TestAction.use_vm_backup, 'vm2-backup1'],
		[TestAction.create_mini_vm, 'vm5', 'network=random', 'cluster=cluster2'],
		[TestAction.delete_volume, 'volume3'],
		[TestAction.expunge_volume, 'volume3'],
		[TestAction.create_mini_vm, 'vm6', 'cluster=cluster1'],
		[TestAction.start_vm, 'vm4'],
		[TestAction.create_vm_backup, 'vm4', 'vm4-backup5'],
		[TestAction.stop_vm, 'vm4'],
		[TestAction.migrate_vm, 'vm3'],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.use_vm_backup, 'vm4-backup5'],
])




'''
The final status:
Running:['vm6']
Stopped:['vm4', 'vm5', 'vm3', 'vm2']
Enadbled:['vm2-backup1', 'vm3-backup3', 'volume2-backup3', 'vm4-backup5', 'vm3-image1']
attached:['volume2']
Detached:['auto-volume1', 'volume4']
Deleted:['volume2-backup2']
Expunged:['vm1', 'volume3', 'image2']
Ha:[]
Group:
	vm_backup2:['vm3-backup3', 'volume2-backup3']---vm3@volume2
	vm_backup3:['vm4-backup5']---vm4@
	vm_backup1:['vm2-backup1']---vm2@
'''