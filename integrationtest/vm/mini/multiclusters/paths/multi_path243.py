import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", checking_point=1, faild_point=100000, path_list=[
		[TestAction.create_mini_vm, 'vm1', 'cluster=cluster1'],
		[TestAction.create_mini_vm, 'vm2', 'cluster=cluster2'],
		[TestAction.create_vm_backup, 'vm2', 'vm2-backup1'],
		[TestAction.create_mini_vm, 'vm3', 'memory=random', 'cluster=cluster1'],
		[TestAction.resize_volume, 'vm2', 5*1024*1024],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.create_volume, 'volume1', 'size=random', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.create_volume, 'volume2', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.delete_volume, 'volume2'],
		[TestAction.recover_volume, 'volume2'],
		[TestAction.add_image, 'image1', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.delete_vm_backup, 'vm2-backup1'],
		[TestAction.delete_image, 'image1'],
		[TestAction.recover_image, 'image1'],
		[TestAction.delete_image, 'image1'],
		[TestAction.expunge_image, 'image1'],
		[TestAction.create_vm_backup, 'vm2', 'vm2-backup2'],
		[TestAction.destroy_vm, 'vm3'],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.resize_data_volume, 'volume2', 5*1024*1024],
		[TestAction.attach_volume, 'vm2', 'volume2'],
		[TestAction.detach_volume, 'volume2'],
		[TestAction.create_volume, 'volume3', 'cluster=cluster2', 'flag=thin,scsi'],
		[TestAction.attach_volume, 'vm1', 'volume1'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.create_volume_backup, 'volume1', 'volume1-backup3'],
		[TestAction.delete_volume_backup, 'volume1-backup3'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.detach_volume, 'volume1'],
		[TestAction.create_mini_vm, 'vm4', 'network=random', 'cluster=cluster1'],
		[TestAction.delete_volume, 'volume3'],
		[TestAction.expunge_volume, 'volume3'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.reboot_vm, 'vm1'],
		[TestAction.start_vm, 'vm2'],
		[TestAction.create_vm_backup, 'vm2', 'vm2-backup4'],
		[TestAction.stop_vm, 'vm2'],
		[TestAction.start_vm, 'vm2'],
		[TestAction.migrate_vm, 'vm2'],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.attach_volume, 'vm2', 'volume2'],
		[TestAction.start_vm, 'vm2'],
		[TestAction.create_volume_backup, 'volume2', 'volume2-backup5'],
		[TestAction.stop_vm, 'vm2'],
		[TestAction.use_volume_backup, 'volume2-backup5'],
		[TestAction.detach_volume, 'volume2'],
])




'''
The final status:
Running:['vm4', 'vm1']
Stopped:['vm2']
Enadbled:['vm2-backup2', 'vm2-backup4', 'volume2-backup5']
attached:[]
Detached:['volume1', 'volume2']
Deleted:['vm3', 'vm2-backup1', 'volume1-backup3']
Expunged:['volume3', 'image1']
Ha:[]
Group:
	vm_backup2:['vm2-backup4']---vm2@
	vm_backup1:['vm2-backup2']---vm2@
'''