import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", checking_point=1, faild_point=100000, path_list=[
		[TestAction.create_mini_vm, 'vm1', 'cluster=cluster1'],
		[TestAction.destroy_vm, 'vm1'],
		[TestAction.recover_vm, 'vm1'],
		[TestAction.create_volume, 'volume1', 'flag=scsi'],
		[TestAction.attach_volume, 'vm1', 'volume1'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.create_volume_backup, 'volume1', 'volume1-backup1'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.detach_volume, 'volume1'],
		[TestAction.create_mini_vm, 'vm2', 'memory=random', 'cluster=cluster1'],
		[TestAction.create_volume, 'volume2', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.resize_data_volume, 'volume2', 5*1024*1024],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.create_volume, 'volume3', 'size=random', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.create_volume, 'volume4', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.delete_volume, 'volume4'],
		[TestAction.add_image, 'image1', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.create_vm_backup, 'vm2', 'vm2-backup2'],
		[TestAction.delete_vm_backup, 'vm2-backup2'],
		[TestAction.delete_image, 'image1'],
		[TestAction.recover_image, 'image1'],
		[TestAction.delete_image, 'image1'],
		[TestAction.expunge_image, 'image1'],
		[TestAction.create_mini_vm, 'vm3', 'cluster=cluster2'],
		[TestAction.create_vm_backup, 'vm3', 'vm3-backup3'],
		[TestAction.change_vm_ha, 'vm2'],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.create_image_from_volume, 'vm2', 'vm2-image2'],
		[TestAction.create_volume, 'volume5', 'size=random', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.create_volume, 'volume6', 'cluster=cluster2', 'flag=thin,scsi'],
		[TestAction.delete_volume_backup, 'volume1-backup1'],
		[TestAction.start_vm, 'vm3'],
		[TestAction.stop_vm, 'vm3'],
		[TestAction.delete_volume, 'volume5'],
		[TestAction.expunge_volume, 'volume5'],
		[TestAction.add_image, 'image3', 'root', os.environ.get('isoForVmUrl')],
		[TestAction.create_vm_by_image, 'image3', 'iso', 'vm4', 'cluster=cluster2'],
		[TestAction.create_vm_backup, 'vm4', 'vm4-backup4'],
		[TestAction.create_image_from_volume, 'vm1', 'vm1-image4'],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.use_vm_backup, 'vm4-backup4'],
])




'''
The final status:
Running:['vm2']
Stopped:['vm4', 'vm3', 'vm1']
Enadbled:['vm3-backup3', 'vm4-backup4', 'vm2-image2', 'image3', 'vm1-image4']
attached:[]
Detached:['volume1', 'volume2', 'volume3', 'volume6']
Deleted:['volume4', 'vm2-backup2', 'volume1-backup1']
Expunged:['volume5', 'image1']
Ha:['vm2']
Group:
	vm_backup2:['vm4-backup4']---vm4@
	vm_backup1:['vm3-backup3']---vm3@
'''