import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", checking_point=1, faild_point=100000, path_list=[
		[TestAction.add_image, 'image1', 'root', os.environ.get('isoForVmUrl')],
		[TestAction.create_vm_by_image, 'image1', 'iso', 'vm1', 'cluster=cluster2'],
		[TestAction.create_volume, 'volume1', 'flag=scsi'],
		[TestAction.attach_volume, 'vm1', 'volume1'],
		[TestAction.create_volume_backup, 'volume1', 'volume1-backup1'],
		[TestAction.detach_volume, 'volume1'],
		[TestAction.create_mini_vm, 'vm2', 'cluster=cluster2'],
		[TestAction.start_vm, 'vm2'],
		[TestAction.create_image_from_volume, 'vm2', 'vm2-image2'],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.create_volume, 'volume2', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.attach_volume, 'vm2', 'volume2'],
		[TestAction.create_volume, 'volume3', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.delete_volume, 'volume3'],
		[TestAction.add_image, 'image3', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.create_vm_backup, 'vm1', 'vm1-backup2'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.use_vm_backup, 'vm1-backup2'],
		[TestAction.delete_image, 'vm2-image2'],
		[TestAction.recover_image, 'vm2-image2'],
		[TestAction.delete_image, 'image3'],
		[TestAction.expunge_image, 'image3'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.create_vm_backup, 'vm1', 'vm1-backup3'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.create_mini_vm, 'vm3', 'cluster=cluster1'],
		[TestAction.change_vm_ha, 'vm3'],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.resize_volume, 'vm3', 5*1024*1024],
		[TestAction.create_volume, 'volume4', 'size=random', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.create_volume, 'volume5', 'cluster=cluster2', 'flag=thick,scsi'],
		[TestAction.delete_volume_backup, 'volume1-backup1'],
		[TestAction.create_mini_vm, 'vm4', 'network=random', 'cluster=cluster2'],
		[TestAction.expunge_volume, 'volume3'],
		[TestAction.create_mini_vm, 'vm5', 'data_volume=true', 'cluster=cluster2'],
		[TestAction.create_vm_backup, 'vm5', 'vm5-backup4'],
		[TestAction.migrate_vm, 'vm3'],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.attach_volume, 'vm3', 'volume5'],
		[TestAction.create_volume_backup, 'volume5', 'volume5-backup6'],
		[TestAction.change_vm_ha, 'vm3'],
		[TestAction.stop_vm, 'vm3'],
		[TestAction.use_volume_backup, 'volume5-backup6'],
		[TestAction.start_vm, 'vm3'],
		[TestAction.change_vm_ha, 'vm3'],
		[TestAction.detach_volume, 'volume5'],
])




'''
The final status:
Running:['vm3']
Stopped:['vm2', 'vm1', 'vm4', 'vm5']
Enadbled:['vm1-backup2', 'vm1-backup3', 'vm5-backup4', 'auto-volume5-backup4', 'volume5-backup6', 'image1', 'vm2-image2']
attached:['volume2', 'auto-volume5']
Detached:['volume1', 'volume4', 'volume5']
Deleted:['volume1-backup1']
Expunged:['volume3', 'image3']
Ha:['vm3']
Group:
	vm_backup2:['vm1-backup3']---vm1@
	vm_backup3:['vm5-backup4', 'auto-volume5-backup4']---vm5@auto-volume5
	vm_backup1:['vm1-backup2']---vm1@
'''