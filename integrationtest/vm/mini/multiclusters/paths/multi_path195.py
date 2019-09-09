import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", checking_point=1, faild_point=100000, path_list=[
		[TestAction.add_image, 'image1', 'root', os.environ.get('isoForVmUrl')],
		[TestAction.create_vm_by_image, 'image1', 'iso', 'vm1', 'cluster=cluster2'],
		[TestAction.create_volume, 'volume1', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.attach_volume, 'vm1', 'volume1'],
		[TestAction.create_volume_backup, 'volume1', 'volume1-backup1'],
		[TestAction.create_mini_vm, 'vm2', 'cluster=cluster2'],
		[TestAction.stop_vm, 'vm2'],
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
		[TestAction.delete_image, 'image1'],
		[TestAction.recover_image, 'image1'],
		[TestAction.delete_image, 'vm2-image2'],
		[TestAction.expunge_image, 'vm2-image2'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.create_vm_backup, 'vm1', 'vm1-backup4'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.create_mini_vm, 'vm3', 'cluster=cluster1'],
		[TestAction.change_vm_ha, 'vm3'],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.resize_volume, 'vm2', 5*1024*1024],
		[TestAction.create_volume, 'volume4', 'size=random', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.create_volume, 'volume5', 'cluster=cluster2', 'flag=thick,scsi'],
		[TestAction.attach_volume, 'vm1', 'volume5'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.create_volume_backup, 'volume5', 'volume5-backup6'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.delete_volume_backup, 'volume5-backup6'],
		[TestAction.create_mini_vm, 'vm4', 'network=random', 'cluster=cluster2'],
		[TestAction.expunge_volume, 'volume3'],
		[TestAction.create_mini_vm, 'vm5', 'data_volume=true', 'cluster=cluster2'],
		[TestAction.create_vm_backup, 'vm5', 'vm5-backup7'],
		[TestAction.migrate_vm, 'vm3'],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.create_volume, 'volume7', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.attach_volume, 'vm3', 'volume7'],
		[TestAction.create_volume_backup, 'volume7', 'volume7-backup9'],
		[TestAction.change_vm_ha, 'vm3'],
		[TestAction.stop_vm, 'vm3'],
		[TestAction.use_volume_backup, 'volume7-backup9'],
		[TestAction.start_vm, 'vm3'],
		[TestAction.change_vm_ha, 'vm3'],
])




'''
The final status:
Running:['vm3']
Stopped:['vm2', 'vm1', 'vm4', 'vm5']
Enadbled:['volume1-backup1', 'vm1-backup2', 'volume1-backup2', 'vm1-backup4', 'volume1-backup4', 'vm5-backup7', 'auto-volume5-backup7', 'volume7-backup9', 'image3', 'image1']
attached:['volume1', 'volume2', 'volume5', 'auto-volume5', 'volume7']
Detached:['volume4']
Deleted:['volume5-backup6']
Expunged:['volume3', 'vm2-image2']
Ha:['vm3']
Group:
	vm_backup2:['vm1-backup4', 'volume1-backup4']---vm1@volume1
	vm_backup3:['vm5-backup7', 'auto-volume5-backup7']---vm5@auto-volume5
	vm_backup1:['vm1-backup2', 'volume1-backup2']---vm1@volume1
'''