import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", checking_point=1, faild_point=100000, path_list=[
		[TestAction.create_mini_vm, 'vm1', 'cluster=cluster2'],
		[TestAction.reboot_vm, 'vm1'],
		[TestAction.create_mini_vm, 'vm2', 'cluster=cluster1'],
		[TestAction.create_vm_backup, 'vm2', 'vm2-backup1'],
		[TestAction.create_mini_vm, 'vm3', 'memory=random', 'cluster=cluster2'],
		[TestAction.resize_volume, 'vm2', 5*1024*1024],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.create_volume, 'volume1', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.attach_volume, 'vm2', 'volume1'],
		[TestAction.detach_volume, 'volume1'],
		[TestAction.create_volume, 'volume2', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.delete_volume, 'volume2'],
		[TestAction.add_image, 'image1', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.recover_volume, 'volume2'],
		[TestAction.attach_volume, 'vm2', 'volume2'],
		[TestAction.start_vm, 'vm2'],
		[TestAction.create_volume_backup, 'volume2', 'volume2-backup2'],
		[TestAction.stop_vm, 'vm2'],
		[TestAction.use_volume_backup, 'volume2-backup2'],
		[TestAction.detach_volume, 'volume2'],
		[TestAction.delete_image, 'image1'],
		[TestAction.recover_image, 'image1'],
		[TestAction.delete_image, 'image1'],
		[TestAction.expunge_image, 'image1'],
		[TestAction.attach_volume, 'vm2', 'volume1'],
		[TestAction.start_vm, 'vm2'],
		[TestAction.create_volume_backup, 'volume1', 'volume1-backup3'],
		[TestAction.stop_vm, 'vm2'],
		[TestAction.detach_volume, 'volume1'],
		[TestAction.destroy_vm, 'vm3'],
		[TestAction.recover_vm, 'vm3'],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.create_image_from_volume, 'vm3', 'vm3-image2'],
		[TestAction.create_volume, 'volume3', 'size=random', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.delete_volume, 'volume1'],
		[TestAction.recover_volume, 'volume1'],
		[TestAction.use_vm_backup, 'vm2-backup1'],
		[TestAction.create_mini_vm, 'vm4', 'memory=random', 'cluster=cluster1'],
		[TestAction.delete_volume, 'volume1'],
		[TestAction.expunge_volume, 'volume1'],
		[TestAction.change_vm_ha, 'vm2'],
		[TestAction.create_vm_backup, 'vm2', 'vm2-backup4'],
		[TestAction.migrate_vm, 'vm4'],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.start_vm, 'vm4'],
		[TestAction.create_vm_backup, 'vm4', 'vm4-backup5'],
		[TestAction.stop_vm, 'vm4'],
		[TestAction.use_vm_backup, 'vm4-backup5'],
])




'''
The final status:
Running:['vm2']
Stopped:['vm1', 'vm3', 'vm4']
Enadbled:['vm2-backup1', 'volume2-backup2', 'volume1-backup3', 'vm2-backup4', 'vm4-backup5', 'vm3-image2']
attached:[]
Detached:['volume2', 'volume3']
Deleted:[]
Expunged:['volume1', 'image1']
Ha:['vm2']
Group:
	vm_backup2:['vm2-backup4']---vm2@
	vm_backup3:['vm4-backup5']---vm4@
	vm_backup1:['vm2-backup1']---vm2@
'''