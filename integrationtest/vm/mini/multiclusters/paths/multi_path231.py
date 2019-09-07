import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", checking_point=1, faild_point=100000, path_list=[
		[TestAction.create_mini_vm, 'vm1', 'data_volume=true', 'cluster=cluster1'],
		[TestAction.create_volume_backup, 'auto-volume1', 'auto-volume1-backup1'],
		[TestAction.create_mini_vm, 'vm2', 'cpu=random', 'cluster=cluster2'],
		[TestAction.create_image_from_volume, 'vm2', 'vm2-image1'],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.create_volume, 'volume2', 'size=random', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.create_volume, 'volume3', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.delete_volume, 'volume3'],
		[TestAction.add_image, 'image2', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.start_vm, 'vm2'],
		[TestAction.create_vm_backup, 'vm2', 'vm2-backup2'],
		[TestAction.stop_vm, 'vm2'],
		[TestAction.use_vm_backup, 'vm2-backup2'],
		[TestAction.delete_image, 'image2'],
		[TestAction.expunge_image, 'image2'],
		[TestAction.create_vm_backup, 'vm1', 'vm1-backup3'],
		[TestAction.add_image, 'image3', 'root', os.environ.get('isoForVmUrl')],
		[TestAction.create_vm_by_image, 'image3', 'iso', 'vm3', 'cluster=cluster1'],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.create_image_from_volume, 'vm1', 'vm1-image4'],
		[TestAction.create_volume, 'volume4', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.attach_volume, 'vm1', 'volume4'],
		[TestAction.detach_volume, 'volume4'],
		[TestAction.create_volume, 'volume5', 'cluster=cluster1', 'flag=thick,scsi'],
		[TestAction.use_volume_backup, 'auto-volume1-backup1'],
		[TestAction.create_mini_vm, 'vm4', 'cpu=random', 'cluster=cluster1'],
		[TestAction.delete_volume, 'volume2'],
		[TestAction.expunge_volume, 'volume2'],
		[TestAction.create_vm_by_image, 'image3', 'iso', 'vm5', 'cluster=cluster2'],
		[TestAction.create_vm_backup, 'vm5', 'vm5-backup5'],
		[TestAction.start_vm, 'vm2'],
		[TestAction.migrate_vm, 'vm2'],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.use_vm_backup, 'vm1-backup3'],
])




'''
The final status:
Running:['vm5', 'vm2']
Stopped:['vm4', 'vm1', 'vm3']
Enadbled:['auto-volume1-backup1', 'vm2-backup2', 'vm1-backup3', 'auto-volume1-backup3', 'vm5-backup5', 'vm2-image1', 'image3', 'vm1-image4']
attached:['auto-volume1']
Detached:['volume4', 'volume5']
Deleted:['volume3']
Expunged:['volume2', 'image2']
Ha:[]
Group:
	vm_backup2:['vm1-backup3', 'auto-volume1-backup3']---vm1@auto-volume1
	vm_backup3:['vm5-backup5']---vm5@
	vm_backup1:['vm2-backup2']---vm2@
'''