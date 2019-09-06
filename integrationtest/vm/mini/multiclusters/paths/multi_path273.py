import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", checking_point=1, faild_point=100000, path_list=[
		[TestAction.create_mini_vm, 'vm1', 'cluster=cluster2'],
		[TestAction.create_vm_backup, 'vm1', 'vm1-backup1'],
		[TestAction.create_mini_vm, 'vm2', 'network=random', 'cluster=cluster1'],
		[TestAction.create_image_from_volume, 'vm1', 'vm1-image1'],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.create_volume, 'volume1', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.attach_volume, 'vm1', 'volume1'],
		[TestAction.create_volume, 'volume2', 'cluster=cluster2', 'flag=thin,scsi'],
		[TestAction.add_image, 'image2', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.attach_volume, 'vm1', 'volume2'],
		[TestAction.create_volume_backup, 'volume2', 'volume2-backup2'],
		[TestAction.delete_volume_backup, 'volume2-backup2'],
		[TestAction.detach_volume, 'volume2'],
		[TestAction.delete_image, 'vm1-image1'],
		[TestAction.delete_image, 'image2'],
		[TestAction.expunge_image, 'image2'],
		[TestAction.create_vm_backup, 'vm1', 'vm1-backup3'],
		[TestAction.create_mini_vm, 'vm3', 'data_volume=true', 'cluster=cluster1'],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.migrate_vm, 'vm1'],
		[TestAction.create_volume, 'volume4', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.attach_volume, 'vm2', 'volume4'],
		[TestAction.detach_volume, 'volume4'],
		[TestAction.create_volume, 'volume5', 'cluster=cluster1', 'flag=thin,scsi'],
		[TestAction.create_volume_backup, 'volume1', 'volume1-backup5'],
		[TestAction.delete_volume_backup, 'volume1-backup5'],
		[TestAction.create_mini_vm, 'vm4', 'cluster=cluster1', 'flag=thick'],
		[TestAction.delete_volume, 'volume1'],
		[TestAction.expunge_volume, 'volume1'],
		[TestAction.add_image, 'image3', 'root', os.environ.get('isoForVmUrl')],
		[TestAction.create_vm_by_image, 'image3', 'iso', 'vm5', 'cluster=cluster1'],
		[TestAction.create_vm_backup, 'vm5', 'vm5-backup6'],
		[TestAction.resize_volume, 'vm4', 5*1024*1024],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.delete_vm_backup, 'vm1-backup1'],
])




'''
The final status:
Running:['vm1', 'vm2', 'vm3', 'vm4', 'vm5']
Stopped:[]
Enadbled:['vm1-backup3', 'volume1-backup3', 'vm5-backup6', 'image3']
attached:['auto-volume3']
Detached:['volume2', 'volume4', 'volume5']
Deleted:['volume2-backup2', 'volume1-backup5', 'vm1-backup1', 'vm1-image1']
Expunged:['volume1', 'image2']
Ha:[]
Group:
	vm_backup2:['vm1-backup3', 'volume1-backup3']---vm1@volume1
	vm_backup3:['vm5-backup6']---vm5@
'''