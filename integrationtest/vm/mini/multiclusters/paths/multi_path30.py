import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", checking_point=1, faild_point=100000, path_list=[
		[TestAction.create_mini_vm, 'vm1', 'data_volume=true', 'cluster=cluster2'],
		[TestAction.create_volume_backup, 'auto-volume1', 'auto-volume1-backup1'],
		[TestAction.create_mini_vm, 'vm2', 'cpu=random', 'cluster=cluster2'],
		[TestAction.create_mini_vm, 'vm3', 'cluster=cluster1'],
		[TestAction.create_image_from_volume, 'vm3', 'vm3-image1'],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.create_volume, 'volume2', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.attach_volume, 'vm3', 'volume2'],
		[TestAction.detach_volume, 'volume2'],
		[TestAction.create_volume, 'volume3', 'cluster=cluster1', 'flag=thin,scsi'],
		[TestAction.add_image, 'image2', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.use_volume_backup, 'auto-volume1-backup1'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.delete_image, 'vm3-image1'],
		[TestAction.recover_image, 'vm3-image1'],
		[TestAction.delete_image, 'vm3-image1'],
		[TestAction.expunge_image, 'vm3-image1'],
		[TestAction.create_vm_backup, 'vm3', 'vm3-backup2'],
		[TestAction.add_image, 'image3', 'root', os.environ.get('isoForVmUrl')],
		[TestAction.create_vm_by_image, 'image3', 'iso', 'vm4', 'cluster=cluster1'],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.resize_volume, 'vm3', 5*1024*1024],
		[TestAction.attach_volume, 'vm3', 'volume3'],
		[TestAction.create_volume, 'volume4', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.delete_volume, 'volume4'],
		[TestAction.recover_volume, 'volume4'],
		[TestAction.stop_vm, 'vm3'],
		[TestAction.use_vm_backup, 'vm3-backup2'],
		[TestAction.start_vm, 'vm3'],
		[TestAction.create_mini_vm, 'vm5', 'cluster=cluster1'],
		[TestAction.start_vm, 'vm5'],
		[TestAction.delete_volume, 'volume4'],
		[TestAction.expunge_volume, 'volume4'],
		[TestAction.destroy_vm, 'vm4'],
		[TestAction.recover_vm, 'vm4'],
		[TestAction.create_vm_backup, 'vm3', 'vm3-backup3'],
		[TestAction.create_image_from_volume, 'vm5', 'vm5-image4'],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.start_vm, 'vm4'],
		[TestAction.create_vm_backup, 'vm4', 'vm4-backup5'],
		[TestAction.stop_vm, 'vm4'],
		[TestAction.use_vm_backup, 'vm4-backup5'],
])




'''
The final status:
Running:['vm2', 'vm1', 'vm3', 'vm5']
Stopped:['vm4']
Enadbled:['auto-volume1-backup1', 'vm3-backup2', 'vm3-backup3', 'volume3-backup3', 'vm4-backup5', 'image2', 'image3', 'vm5-image4']
attached:['auto-volume1', 'volume3']
Detached:['volume2']
Deleted:[]
Expunged:['volume4', 'vm3-image1']
Ha:[]
Group:
	vm_backup2:['vm3-backup3', 'volume3-backup3']---vm3@volume3
	vm_backup3:['vm4-backup5']---vm4@
	vm_backup1:['vm3-backup2']---vm3@
'''