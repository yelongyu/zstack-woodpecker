import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", checking_point=1, faild_point=100000, path_list=[
		[TestAction.add_image, 'image1', 'root', os.environ.get('isoForVmUrl')],
		[TestAction.create_vm_by_image, 'image1', 'iso', 'vm1', 'cluster=cluster2'],
		[TestAction.create_mini_vm, 'vm2', 'cluster=cluster1'],
		[TestAction.create_volume, 'volume1', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.attach_volume, 'vm2', 'volume1'],
		[TestAction.create_volume_backup, 'volume1', 'volume1-backup1'],
		[TestAction.create_mini_vm, 'vm3', 'cluster=cluster2'],
		[TestAction.stop_vm, 'vm3'],
		[TestAction.start_vm, 'vm3'],
		[TestAction.create_image_from_volume, 'vm2', 'vm2-image2'],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.create_volume, 'volume2', 'size=random', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.delete_volume, 'volume1'],
		[TestAction.recover_volume, 'volume1'],
		[TestAction.add_image, 'image3', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.attach_volume, 'vm2', 'volume1'],
		[TestAction.start_vm, 'vm2'],
		[TestAction.create_volume_backup, 'volume1', 'volume1-backup2'],
		[TestAction.stop_vm, 'vm2'],
		[TestAction.use_volume_backup, 'volume1-backup2'],
		[TestAction.delete_image, 'image1'],
		[TestAction.recover_image, 'image1'],
		[TestAction.delete_image, 'vm2-image2'],
		[TestAction.expunge_image, 'vm2-image2'],
		[TestAction.create_vm_backup, 'vm3', 'vm3-backup3'],
		[TestAction.create_mini_vm, 'vm4', 'cluster=cluster1'],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.create_image_from_volume, 'vm1', 'vm1-image4'],
		[TestAction.attach_volume, 'vm1', 'volume2'],
		[TestAction.detach_volume, 'volume2'],
		[TestAction.delete_volume, 'volume1'],
		[TestAction.attach_volume, 'vm3', 'volume2'],
		[TestAction.start_vm, 'vm3'],
		[TestAction.create_volume_backup, 'volume2', 'volume2-backup4'],
		[TestAction.stop_vm, 'vm3'],
		[TestAction.use_volume_backup, 'volume2-backup4'],
		[TestAction.start_vm, 'vm2'],
		[TestAction.stop_vm, 'vm2'],
		[TestAction.expunge_volume, 'volume1'],
		[TestAction.change_vm_ha, 'vm4'],
		[TestAction.create_volume, 'volume3', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.attach_volume, 'vm3', 'volume3'],
		[TestAction.start_vm, 'vm3'],
		[TestAction.create_volume_backup, 'volume3', 'volume3-backup5'],
		[TestAction.stop_vm, 'vm3'],
		[TestAction.create_image_from_volume, 'vm4', 'vm4-image5'],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.delete_volume_backup, 'volume2-backup4'],
])




'''
The final status:
Running:['vm4']
Stopped:['vm1', 'vm2', 'vm3']
Enadbled:['volume1-backup1', 'volume1-backup2', 'vm3-backup3', 'volume3-backup5', 'image3', 'image1', 'vm1-image4', 'vm4-image5']
attached:['volume2', 'volume3']
Detached:[]
Deleted:['volume2-backup4']
Expunged:['volume1', 'vm2-image2']
Ha:['vm4']
Group:
	vm_backup1:['vm3-backup3']---vm3@
'''