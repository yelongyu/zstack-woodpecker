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
		[TestAction.create_mini_vm, 'vm2', 'cluster=cluster1'],
		[TestAction.start_vm, 'vm2'],
		[TestAction.stop_vm, 'vm2'],
		[TestAction.create_image_from_volume, 'vm1', 'vm1-image2'],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.create_volume, 'volume2', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.attach_volume, 'vm1', 'volume2'],
		[TestAction.create_volume, 'volume3', 'cluster=cluster2', 'flag=thick,scsi'],
		[TestAction.add_image, 'image3', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.delete_volume_backup, 'volume1-backup1'],
		[TestAction.delete_image, 'image1'],
		[TestAction.recover_image, 'image1'],
		[TestAction.delete_image, 'image3'],
		[TestAction.expunge_image, 'image3'],
		[TestAction.attach_volume, 'vm1', 'volume3'],
		[TestAction.create_volume_backup, 'volume3', 'volume3-backup2'],
		[TestAction.detach_volume, 'volume3'],
		[TestAction.destroy_vm, 'vm2'],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.create_mini_vm, 'vm3', 'cluster=cluster1'],
		[TestAction.resize_volume, 'vm3', 5*1024*1024],
		[TestAction.create_volume, 'volume4', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.attach_volume, 'vm3', 'volume4'],
		[TestAction.detach_volume, 'volume4'],
		[TestAction.create_volume, 'volume5', 'cluster=cluster2', 'flag=thin,scsi'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.create_vm_backup, 'vm1', 'vm1-backup3'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.use_vm_backup, 'vm1-backup3'],
		[TestAction.create_mini_vm, 'vm4', 'cluster=cluster2', 'flag=thin'],
		[TestAction.delete_volume, 'volume5'],
		[TestAction.expunge_volume, 'volume5'],
		[TestAction.create_mini_vm, 'vm5', 'cluster=cluster2'],
		[TestAction.create_vm_backup, 'vm5', 'vm5-backup5'],
		[TestAction.create_image_from_volume, 'vm4', 'vm4-image4'],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.delete_vm_backup, 'vm1-backup3'],
])




'''
The final status:
Running:['vm4', 'vm5']
Stopped:['vm1', 'vm3']
Enadbled:['volume3-backup2', 'vm5-backup5', 'vm1-image2', 'image1', 'vm4-image4']
attached:['volume2']
Detached:['volume1', 'volume3', 'volume4']
Deleted:['vm2', 'volume1-backup1', 'vm1-backup3', 'volume2-backup3']
Expunged:['volume5', 'image3']
Ha:[]
Group:
	vm_backup2:['vm5-backup5']---vm5@
'''