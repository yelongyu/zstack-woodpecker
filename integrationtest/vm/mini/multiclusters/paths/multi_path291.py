import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", checking_point=1, faild_point=100000, path_list=[
		[TestAction.create_mini_vm, 'vm1', 'data_volume=true', 'cluster=cluster1'],
		[TestAction.create_vm_backup, 'vm1', 'vm1-backup1'],
		[TestAction.create_mini_vm, 'vm2', 'cluster=cluster1', 'flag=thick'],
		[TestAction.create_image_from_volume, 'vm2', 'vm2-image1'],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.create_mini_vm, 'vm3', 'cluster=cluster2'],
		[TestAction.create_volume, 'volume2', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.attach_volume, 'vm3', 'volume2'],
		[TestAction.delete_volume, 'volume2'],
		[TestAction.add_image, 'image2', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.create_volume_backup, 'auto-volume1', 'auto-volume1-backup3'],
		[TestAction.delete_volume_backup, 'auto-volume1-backup3'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.delete_image, 'image2'],
		[TestAction.expunge_image, 'image2'],
		[TestAction.create_vm_backup, 'vm3', 'vm3-backup4'],
		[TestAction.change_vm_ha, 'vm3'],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.create_volume, 'volume3', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.resize_data_volume, 'volume3', 5*1024*1024],
		[TestAction.create_volume, 'volume4', 'size=random', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.create_volume, 'volume5', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.delete_volume, 'volume5'],
		[TestAction.attach_volume, 'vm2', 'volume3'],
		[TestAction.start_vm, 'vm2'],
		[TestAction.create_volume_backup, 'volume3', 'volume3-backup5'],
		[TestAction.delete_volume_backup, 'volume3-backup5'],
		[TestAction.stop_vm, 'vm2'],
		[TestAction.detach_volume, 'volume3'],
		[TestAction.create_mini_vm, 'vm4', 'network=random', 'cluster=cluster1'],
		[TestAction.expunge_volume, 'volume5'],
		[TestAction.create_mini_vm, 'vm5', 'data_volume=true', 'cluster=cluster1'],
		[TestAction.attach_volume, 'vm4', 'volume3'],
		[TestAction.create_volume_backup, 'volume3', 'volume3-backup6'],
		[TestAction.detach_volume, 'volume3'],
		[TestAction.migrate_vm, 'vm5'],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.delete_volume_backup, 'volume3-backup6'],
])




'''
The final status:
Running:['vm3', 'vm4', 'vm5']
Stopped:['vm1', 'vm2']
Enadbled:['vm1-backup1', 'auto-volume1-backup1', 'vm3-backup4', 'vm2-image1']
attached:['auto-volume1', 'auto-volume5']
Detached:['volume4', 'volume3']
Deleted:['volume2', 'auto-volume1-backup3', 'volume3-backup5', 'volume3-backup6']
Expunged:['volume5', 'image2']
Ha:['vm3']
Group:
	vm_backup2:['vm3-backup4']---vm3@
	vm_backup1:['vm1-backup1', 'auto-volume1-backup1']---vm1@auto-volume1
'''