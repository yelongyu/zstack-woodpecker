import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", checking_point=1, faild_point=100000, path_list=[
		[TestAction.create_mini_vm, 'vm1', 'cluster=cluster1'],
		[TestAction.change_vm_ha, 'vm1'],
		[TestAction.create_volume, 'volume1', 'flag=scsi'],
		[TestAction.attach_volume, 'vm1', 'volume1'],
		[TestAction.create_volume_backup, 'volume1', 'volume1-backup1'],
		[TestAction.detach_volume, 'volume1'],
		[TestAction.create_mini_vm, 'vm2', 'cluster=cluster1', 'flag=thick'],
		[TestAction.create_image_from_volume, 'vm1', 'vm1-image1'],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.create_volume, 'volume2', 'size=random', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.create_volume, 'volume3', 'cluster=cluster2', 'flag=thin,scsi'],
		[TestAction.add_image, 'image2', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.delete_volume_backup, 'volume1-backup1'],
		[TestAction.delete_image, 'image2'],
		[TestAction.delete_image, 'vm1-image1'],
		[TestAction.expunge_image, 'vm1-image1'],
		[TestAction.create_mini_vm, 'vm3', 'cluster=cluster2'],
		[TestAction.create_vm_backup, 'vm3', 'vm3-backup2'],
		[TestAction.reboot_vm, 'vm3'],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.start_vm, 'vm2'],
		[TestAction.migrate_vm, 'vm2'],
		[TestAction.attach_volume, 'vm3', 'volume3'],
		[TestAction.detach_volume, 'volume3'],
		[TestAction.delete_volume, 'volume2'],
		[TestAction.delete_vm_backup, 'vm3-backup2'],
		[TestAction.destroy_vm, 'vm3'],
		[TestAction.expunge_vm, 'vm3'],
		[TestAction.expunge_volume, 'volume2'],
		[TestAction.change_vm_ha, 'vm2'],
		[TestAction.attach_volume, 'vm1', 'volume3'],
		[TestAction.create_volume_backup, 'volume3', 'volume3-backup3'],
		[TestAction.detach_volume, 'volume3'],
		[TestAction.resize_data_volume, 'volume3', 5*1024*1024],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.delete_volume_backup, 'volume3-backup3'],
])




'''
The final status:
Running:['vm1', 'vm2']
Stopped:[]
Enadbled:[]
attached:[]
Detached:['volume1', 'volume3']
Deleted:['volume1-backup1', 'vm3-backup2', 'volume3-backup3', 'image2']
Expunged:['vm3', 'volume2', 'vm1-image1']
Ha:['vm1', 'vm2']
Group:
'''