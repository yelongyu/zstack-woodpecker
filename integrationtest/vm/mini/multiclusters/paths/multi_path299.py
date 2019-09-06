import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", checking_point=1, faild_point=100000, path_list=[
		[TestAction.create_mini_vm, 'vm1', 'data_volume=true', 'cluster=cluster2'],
		[TestAction.create_volume_backup, 'auto-volume1', 'auto-volume1-backup1'],
		[TestAction.destroy_vm, 'vm1'],
		[TestAction.expunge_vm, 'vm1'],
		[TestAction.create_mini_vm, 'vm2', 'cluster=cluster2'],
		[TestAction.create_image_from_volume, 'vm2', 'vm2-image1'],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.create_volume, 'volume2', 'size=random', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.create_volume, 'volume3', 'cluster=cluster2', 'flag=thin,scsi'],
		[TestAction.add_image, 'image2', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.create_vm_backup, 'vm2', 'vm2-backup2'],
		[TestAction.stop_vm, 'vm2'],
		[TestAction.use_vm_backup, 'vm2-backup2'],
		[TestAction.start_vm, 'vm2'],
		[TestAction.delete_image, 'image2'],
		[TestAction.expunge_image, 'image2'],
		[TestAction.create_mini_vm, 'vm3', 'cluster=cluster1'],
		[TestAction.create_vm_backup, 'vm3', 'vm3-backup3'],
		[TestAction.destroy_vm, 'vm3'],
		[TestAction.recover_vm, 'vm3'],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.start_vm, 'vm2'],
		[TestAction.migrate_vm, 'vm2'],
		[TestAction.create_volume, 'volume4', 'size=random', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.create_volume, 'volume5', 'cluster=cluster2', 'flag=thick,scsi'],
		[TestAction.attach_volume, 'vm3', 'auto-volume1'],
		[TestAction.use_volume_backup, 'auto-volume1-backup1'],
		[TestAction.detach_volume, 'auto-volume1'],
		[TestAction.start_vm, 'vm2'],
		[TestAction.stop_vm, 'vm2'],
		[TestAction.delete_volume, 'volume4'],
		[TestAction.expunge_volume, 'volume4'],
		[TestAction.add_image, 'image3', 'root', os.environ.get('isoForVmUrl')],
		[TestAction.create_vm_by_image, 'image3', 'iso', 'vm4', 'cluster=cluster2'],
		[TestAction.attach_volume, 'vm4', 'volume5'],
		[TestAction.create_volume_backup, 'volume5', 'volume5-backup4'],
		[TestAction.detach_volume, 'volume5'],
		[TestAction.create_volume, 'volume6', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.resize_data_volume, 'volume6', 5*1024*1024],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.delete_volume_backup, 'auto-volume1-backup1'],
])




'''
The final status:
Running:['vm4']
Stopped:['vm3', 'vm2']
Enadbled:['vm2-backup2', 'vm3-backup3', 'volume5-backup4', 'vm2-image1', 'image3']
attached:[]
Detached:['volume2', 'volume3', 'auto-volume1', 'volume5', 'volume6']
Deleted:['auto-volume1-backup1']
Expunged:['vm1', 'volume4', 'image2']
Ha:[]
Group:
	vm_backup2:['vm3-backup3']---vm3@
	vm_backup1:['vm2-backup2']---vm2@
'''