import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", checking_point=1, faild_point=100000, path_list=[
		[TestAction.create_mini_vm, 'vm1', 'cluster=cluster2'],
		[TestAction.reboot_vm, 'vm1'],
		[TestAction.create_volume, 'volume1', 'flag=scsi'],
		[TestAction.attach_volume, 'vm1', 'volume1'],
		[TestAction.create_volume_backup, 'volume1', 'volume1-backup1'],
		[TestAction.detach_volume, 'volume1'],
		[TestAction.create_mini_vm, 'vm2', 'cluster=cluster2'],
		[TestAction.stop_vm, 'vm2'],
		[TestAction.start_vm, 'vm2'],
		[TestAction.create_volume, 'volume2', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.resize_data_volume, 'volume2', 5*1024*1024],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.create_volume, 'volume3', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.attach_volume, 'vm1', 'volume3'],
		[TestAction.detach_volume, 'volume3'],
		[TestAction.delete_volume, 'volume3'],
		[TestAction.add_image, 'image1', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.delete_volume_backup, 'volume1-backup1'],
		[TestAction.delete_image, 'image1'],
		[TestAction.expunge_image, 'image1'],
		[TestAction.create_mini_vm, 'vm3', 'cluster=cluster1'],
		[TestAction.create_vm_backup, 'vm3', 'vm3-backup2'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.reboot_vm, 'vm1'],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.create_image_from_volume, 'vm3', 'vm3-image2'],
		[TestAction.attach_volume, 'vm3', 'volume2'],
		[TestAction.delete_volume, 'volume2'],
		[TestAction.recover_volume, 'volume2'],
		[TestAction.recover_volume, 'volume3'],
		[TestAction.attach_volume, 'vm1', 'volume3'],
		[TestAction.create_volume_backup, 'volume3', 'volume3-backup3'],
		[TestAction.delete_volume_backup, 'volume3-backup3'],
		[TestAction.detach_volume, 'volume3'],
		[TestAction.destroy_vm, 'vm3'],
		[TestAction.expunge_vm, 'vm3'],
		[TestAction.delete_volume, 'volume2'],
		[TestAction.expunge_volume, 'volume2'],
		[TestAction.create_mini_vm, 'vm4', 'data_volume=true', 'cluster=cluster2'],
		[TestAction.create_volume_backup, 'auto-volume4', 'auto-volume4-backup4'],
		[TestAction.create_image_from_volume, 'vm1', 'vm1-image3'],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.create_vm_backup, 'vm1', 'vm1-backup5'],
		[TestAction.delete_vm_backup, 'vm1-backup5'],
		[TestAction.stop_vm, 'vm1'],
])




'''
The final status:
Running:[]
Stopped:['vm2', 'vm4', 'vm1']
Enadbled:['vm3-backup2', 'auto-volume4-backup4', 'vm3-image2', 'vm1-image3']
attached:['auto-volume4']
Detached:['volume1', 'volume3']
Deleted:['volume1-backup1', 'volume3-backup3', 'vm1-backup5']
Expunged:['vm3', 'volume2', 'image1']
Ha:[]
Group:
	vm_backup1:['vm3-backup2']---vm3@
'''