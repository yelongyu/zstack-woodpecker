import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", checking_point=1, faild_point=100000, path_list=[
		[TestAction.create_mini_vm, 'vm1', 'cluster=cluster2'],
		[TestAction.destroy_vm, 'vm1'],
		[TestAction.recover_vm, 'vm1'],
		[TestAction.create_mini_vm, 'vm2', 'cluster=cluster1'],
		[TestAction.create_vm_backup, 'vm2', 'vm2-backup1'],
		[TestAction.destroy_vm, 'vm1'],
		[TestAction.expunge_vm, 'vm1'],
		[TestAction.create_mini_vm, 'vm3', 'cluster=cluster2'],
		[TestAction.resize_volume, 'vm2', 5*1024*1024],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.create_volume, 'volume1', 'size=random', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.create_volume, 'volume2', 'cluster=cluster1', 'flag=thick,scsi'],
		[TestAction.add_image, 'image1', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.start_vm, 'vm3'],
		[TestAction.create_vm_backup, 'vm3', 'vm3-backup2'],
		[TestAction.stop_vm, 'vm3'],
		[TestAction.use_vm_backup, 'vm3-backup2'],
		[TestAction.delete_image, 'image1'],
		[TestAction.recover_image, 'image1'],
		[TestAction.delete_image, 'image1'],
		[TestAction.expunge_image, 'image1'],
		[TestAction.create_vm_backup, 'vm2', 'vm2-backup3'],
		[TestAction.destroy_vm, 'vm3'],
		[TestAction.recover_vm, 'vm3'],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.start_vm, 'vm3'],
		[TestAction.migrate_vm, 'vm3'],
		[TestAction.create_volume, 'volume3', 'size=random', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.create_volume, 'volume4', 'cluster=cluster2', 'flag=thick,scsi'],
		[TestAction.attach_volume, 'vm3', 'volume4'],
		[TestAction.create_volume_backup, 'volume4', 'volume4-backup4'],
		[TestAction.delete_volume_backup, 'volume4-backup4'],
		[TestAction.detach_volume, 'volume4'],
		[TestAction.destroy_vm, 'vm2'],
		[TestAction.expunge_vm, 'vm2'],
		[TestAction.delete_volume, 'volume2'],
		[TestAction.expunge_volume, 'volume2'],
		[TestAction.create_mini_vm, 'vm4', 'cluster=cluster1'],
		[TestAction.destroy_vm, 'vm4'],
		[TestAction.create_mini_vm, 'vm5', 'cluster=cluster1'],
		[TestAction.create_vm_backup, 'vm5', 'vm5-backup5'],
		[TestAction.migrate_vm, 'vm3'],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.use_vm_backup, 'vm5-backup5'],
])




'''
The final status:
Running:['vm3']
Stopped:['vm5']
Enadbled:['vm2-backup1', 'vm3-backup2', 'vm2-backup3', 'vm5-backup5']
attached:[]
Detached:['volume1', 'volume3', 'volume4']
Deleted:['vm4', 'volume4-backup4']
Expunged:['vm1', 'vm2', 'volume2', 'image1']
Ha:[]
Group:
	vm_backup2:['vm3-backup2']---vm3@
	vm_backup3:['vm2-backup3']---vm2@
	vm_backup1:['vm2-backup1']---vm2@
	vm_backup4:['vm5-backup5']---vm5@
'''