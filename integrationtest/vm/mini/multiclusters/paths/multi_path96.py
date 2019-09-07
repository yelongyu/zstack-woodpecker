import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", checking_point=1, faild_point=100000, path_list=[
		[TestAction.create_mini_vm, 'vm1', 'cluster=cluster1'],
		[TestAction.destroy_vm, 'vm1'],
		[TestAction.create_volume, 'volume1', 'flag=scsi'],
		[TestAction.create_mini_vm, 'vm2', ],
		[TestAction.attach_volume, 'vm2', 'volume1'],
		[TestAction.create_volume_backup, 'volume1', 'volume1-backup1'],
		[TestAction.detach_volume, 'volume1'],
		[TestAction.create_mini_vm, 'vm3', 'network=random', 'cluster=cluster2'],
		[TestAction.create_image_from_volume, 'vm3', 'vm3-image1'],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.create_volume, 'volume2', 'size=random', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.create_volume, 'volume3', 'cluster=cluster1', 'flag=thick,scsi'],
		[TestAction.add_image, 'image2', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.create_vm_backup, 'vm2', 'vm2-backup2'],
		[TestAction.stop_vm, 'vm2'],
		[TestAction.use_vm_backup, 'vm2-backup2'],
		[TestAction.start_vm, 'vm2'],
		[TestAction.delete_image, 'vm3-image1'],
		[TestAction.recover_image, 'vm3-image1'],
		[TestAction.delete_image, 'vm3-image1'],
		[TestAction.expunge_image, 'vm3-image1'],
		[TestAction.attach_volume, 'vm3', 'volume3'],
		[TestAction.create_volume_backup, 'volume3', 'volume3-backup3'],
		[TestAction.detach_volume, 'volume3'],
		[TestAction.change_vm_ha, 'vm3'],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.create_image_from_volume, 'vm3', 'vm3-image3'],
		[TestAction.attach_volume, 'vm3', 'volume2'],
		[TestAction.create_volume, 'volume4', 'cluster=cluster2', 'flag=thin,scsi'],
		[TestAction.attach_volume, 'vm2', 'volume3'],
		[TestAction.stop_vm, 'vm2'],
		[TestAction.use_volume_backup, 'volume3-backup3'],
		[TestAction.start_vm, 'vm2'],
		[TestAction.detach_volume, 'volume3'],
		[TestAction.create_mini_vm, 'vm4', 'network=random', 'cluster=cluster2'],
		[TestAction.delete_volume, 'volume4'],
		[TestAction.expunge_volume, 'volume4'],
		[TestAction.add_image, 'image4', 'root', os.environ.get('isoForVmUrl')],
		[TestAction.create_vm_by_image, 'image4', 'iso', 'vm5', 'cluster=cluster1'],
		[TestAction.create_vm_backup, 'vm5', 'vm5-backup4'],
		[TestAction.create_image_from_volume, 'vm5', 'vm5-image5'],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.use_vm_backup, 'vm5-backup4'],
])




'''
The final status:
Running:['vm3', 'vm2', 'vm4']
Stopped:['vm5']
Enadbled:['volume1-backup1', 'vm2-backup2', 'volume3-backup3', 'vm5-backup4', 'image2', 'vm3-image3', 'image4', 'vm5-image5']
attached:['volume2']
Detached:['volume1', 'volume3']
Deleted:['vm1']
Expunged:['volume4', 'vm3-image1']
Ha:['vm3']
Group:
	vm_backup2:['vm5-backup4']---vm5@
	vm_backup1:['vm2-backup2']---vm2@
'''