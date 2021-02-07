import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", checking_point=1, faild_point=100000, path_list=[
		[TestAction.create_mini_vm, 'vm1', 'cluster=cluster2'],
		[TestAction.reboot_vm, 'vm1'],
		[TestAction.create_vm_backup, 'vm1', 'vm1-backup1'],
		[TestAction.create_mini_vm, 'vm2', 'cpu=random', 'cluster=cluster1'],
		[TestAction.migrate_vm, 'vm1'],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.create_volume, 'volume1', 'size=random', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.create_volume, 'volume2', 'cluster=cluster2', 'flag=thick,scsi'],
		[TestAction.add_image, 'image1', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.delete_vm_backup, 'vm1-backup1'],
		[TestAction.delete_image, 'image1'],
		[TestAction.recover_image, 'image1'],
		[TestAction.delete_image, 'image1'],
		[TestAction.expunge_image, 'image1'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.create_vm_backup, 'vm1', 'vm1-backup2'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.change_vm_ha, 'vm2'],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.resize_data_volume, 'volume1', 5*1024*1024],
		[TestAction.attach_volume, 'vm1', 'volume1'],
		[TestAction.detach_volume, 'volume1'],
		[TestAction.create_volume, 'volume3', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.delete_volume, 'volume3'],
		[TestAction.create_volume, 'volume4', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.attach_volume, 'vm2', 'volume4'],
		[TestAction.create_volume_backup, 'volume4', 'volume4-backup3'],
		[TestAction.change_vm_ha, 'vm2'],
		[TestAction.stop_vm, 'vm2'],
		[TestAction.use_volume_backup, 'volume4-backup3'],
		[TestAction.start_vm, 'vm2'],
		[TestAction.change_vm_ha, 'vm2'],
		[TestAction.create_mini_vm, 'vm3', 'memory=random', 'cluster=cluster2'],
		[TestAction.delete_volume, 'volume1'],
		[TestAction.expunge_volume, 'volume1'],
		[TestAction.destroy_vm, 'vm2'],
		[TestAction.recover_vm, 'vm2'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.create_vm_backup, 'vm1', 'vm1-backup4'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.create_image_from_volume, 'vm1', 'vm1-image2'],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.attach_volume, 'vm2', 'volume4'],
		[TestAction.start_vm, 'vm2'],
		[TestAction.create_volume_backup, 'volume4', 'volume4-backup5'],
		[TestAction.stop_vm, 'vm2'],
		[TestAction.use_volume_backup, 'volume4-backup5'],
])




'''
The final status:
Running:[]
Stopped:['vm1', 'vm3', 'vm2']
Enadbled:['vm1-backup2', 'volume4-backup3', 'vm1-backup4', 'volume4-backup5', 'vm1-image2']
attached:['volume4']
Detached:['volume2']
Deleted:['volume3', 'vm1-backup1']
Expunged:['volume1', 'image1']
Ha:[]
Group:
	vm_backup2:['vm1-backup4']---vm1@
	vm_backup1:['vm1-backup2']---vm1@
'''