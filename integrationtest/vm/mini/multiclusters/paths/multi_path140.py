import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", checking_point=1, faild_point=100000, path_list=[
		[TestAction.create_mini_vm, 'vm1', 'cluster=cluster1'],
		[TestAction.reboot_vm, 'vm1'],
		[TestAction.create_vm_backup, 'vm1', 'vm1-backup1'],
		[TestAction.create_mini_vm, 'vm2', 'cluster=cluster1', 'flag=thick'],
		[TestAction.create_image_from_volume, 'vm2', 'vm2-image1'],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.create_volume, 'volume1', 'size=random', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.delete_volume, 'volume1'],
		[TestAction.recover_volume, 'volume1'],
		[TestAction.add_image, 'image2', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.delete_vm_backup, 'vm1-backup1'],
		[TestAction.delete_image, 'vm2-image1'],
		[TestAction.recover_image, 'vm2-image1'],
		[TestAction.delete_image, 'image2'],
		[TestAction.expunge_image, 'image2'],
		[TestAction.create_mini_vm, 'vm3', 'cluster=cluster2'],
		[TestAction.create_vm_backup, 'vm3', 'vm3-backup2'],
		[TestAction.start_vm, 'vm2'],
		[TestAction.reboot_vm, 'vm2'],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.migrate_vm, 'vm1'],
		[TestAction.attach_volume, 'vm2', 'volume1'],
		[TestAction.create_volume, 'volume2', 'cluster=cluster1', 'flag=thick,scsi'],
		[TestAction.create_volume_backup, 'volume1', 'volume1-backup3'],
		[TestAction.stop_vm, 'vm2'],
		[TestAction.use_volume_backup, 'volume1-backup3'],
		[TestAction.start_vm, 'vm2'],
		[TestAction.start_vm, 'vm3'],
		[TestAction.delete_volume, 'volume1'],
		[TestAction.expunge_volume, 'volume1'],
		[TestAction.create_mini_vm, 'vm4', 'data_volume=true', 'cluster=cluster1'],
		[TestAction.create_vm_backup, 'vm3', 'vm3-backup4'],
		[TestAction.migrate_vm, 'vm3'],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.start_vm, 'vm4'],
		[TestAction.create_volume_backup, 'auto-volume4', 'auto-volume4-backup5'],
		[TestAction.stop_vm, 'vm4'],
		[TestAction.use_volume_backup, 'auto-volume4-backup5'],
])




'''
The final status:
Running:['vm3']
Stopped:['vm1', 'vm2', 'vm4']
Enadbled:['vm3-backup2', 'volume1-backup3', 'vm3-backup4', 'auto-volume4-backup5', 'vm2-image1']
attached:['auto-volume4']
Detached:['volume2']
Deleted:['vm1-backup1']
Expunged:['volume1', 'image2']
Ha:[]
Group:
	vm_backup2:['vm3-backup4']---vm3@
	vm_backup1:['vm3-backup2']---vm3@
'''