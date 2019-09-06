import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", checking_point=1, faild_point=100000, path_list=[
		[TestAction.add_image, 'image1', 'root', os.environ.get('isoForVmUrl')],
		[TestAction.create_vm_by_image, 'image1', 'iso', 'vm1', 'cluster=cluster2'],
		[TestAction.create_vm_backup, 'vm1', 'vm1-backup1'],
		[TestAction.create_mini_vm, 'vm2', 'cluster=cluster2'],
		[TestAction.start_vm, 'vm2'],
		[TestAction.create_volume, 'volume1', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.resize_data_volume, 'volume1', 5*1024*1024],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.attach_volume, 'vm1', 'volume1'],
		[TestAction.detach_volume, 'volume1'],
		[TestAction.create_volume, 'volume2', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.delete_volume, 'volume2'],
		[TestAction.add_image, 'image2', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.attach_volume, 'vm2', 'volume1'],
		[TestAction.start_vm, 'vm2'],
		[TestAction.create_volume_backup, 'volume1', 'volume1-backup2'],
		[TestAction.delete_volume_backup, 'volume1-backup2'],
		[TestAction.stop_vm, 'vm2'],
		[TestAction.detach_volume, 'volume1'],
		[TestAction.delete_image, 'image2'],
		[TestAction.recover_image, 'image2'],
		[TestAction.delete_image, 'image2'],
		[TestAction.expunge_image, 'image2'],
		[TestAction.start_vm, 'vm2'],
		[TestAction.create_vm_backup, 'vm2', 'vm2-backup3'],
		[TestAction.stop_vm, 'vm2'],
		[TestAction.create_mini_vm, 'vm3', 'data_volume=true', 'cluster=cluster1'],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.create_image_from_volume, 'vm1', 'vm1-image3'],
		[TestAction.attach_volume, 'vm2', 'volume1'],
		[TestAction.create_volume, 'volume4', 'cluster=cluster2', 'flag=thick,scsi'],
		[TestAction.start_vm, 'vm2'],
		[TestAction.create_volume_backup, 'volume1', 'volume1-backup4'],
		[TestAction.delete_volume_backup, 'volume1-backup4'],
		[TestAction.stop_vm, 'vm2'],
		[TestAction.create_mini_vm, 'vm4', 'cluster=cluster2', 'flag=thick'],
		[TestAction.expunge_volume, 'volume2'],
		[TestAction.create_mini_vm, 'vm5', 'cluster=cluster1'],
		[TestAction.start_vm, 'vm2'],
		[TestAction.create_volume_backup, 'volume1', 'volume1-backup5'],
		[TestAction.stop_vm, 'vm2'],
		[TestAction.create_image_from_volume, 'vm3', 'vm3-image4'],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.use_volume_backup, 'volume1-backup5'],
])




'''
The final status:
Running:['vm3', 'vm5']
Stopped:['vm1', 'vm2', 'vm4']
Enadbled:['vm1-backup1', 'vm2-backup3', 'volume1-backup5', 'image1', 'vm1-image3', 'vm3-image4']
attached:['auto-volume3', 'volume1']
Detached:['volume4']
Deleted:['volume1-backup2', 'volume1-backup4']
Expunged:['volume2', 'image2']
Ha:[]
Group:
	vm_backup2:['vm2-backup3']---vm2@
	vm_backup1:['vm1-backup1']---vm1@
'''