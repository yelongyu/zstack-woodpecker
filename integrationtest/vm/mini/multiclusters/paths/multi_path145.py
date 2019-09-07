import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", checking_point=1, faild_point=100000, path_list=[
		[TestAction.create_mini_vm, 'vm1', 'cluster=cluster2'],
		[TestAction.destroy_vm, 'vm1'],
		[TestAction.recover_vm, 'vm1'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.create_vm_backup, 'vm1', 'vm1-backup1'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.create_mini_vm, 'vm2', 'cpu=random', 'cluster=cluster1'],
		[TestAction.migrate_vm, 'vm2'],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.create_volume, 'volume1', 'size=random', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.create_volume, 'volume2', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.delete_volume, 'volume2'],
		[TestAction.recover_volume, 'volume2'],
		[TestAction.add_image, 'image1', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.use_vm_backup, 'vm1-backup1'],
		[TestAction.delete_image, 'image1'],
		[TestAction.expunge_image, 'image1'],
		[TestAction.attach_volume, 'vm2', 'volume2'],
		[TestAction.create_volume_backup, 'volume2', 'volume2-backup2'],
		[TestAction.detach_volume, 'volume2'],
		[TestAction.add_image, 'image2', 'root', os.environ.get('isoForVmUrl')],
		[TestAction.create_vm_by_image, 'image2', 'iso', 'vm3', 'cluster=cluster1'],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.migrate_vm, 'vm1'],
		[TestAction.attach_volume, 'vm2', 'volume1'],
		[TestAction.delete_volume, 'volume2'],
		[TestAction.recover_volume, 'volume2'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.use_vm_backup, 'vm1-backup1'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.delete_volume, 'volume1'],
		[TestAction.expunge_volume, 'volume1'],
		[TestAction.change_vm_ha, 'vm2'],
		[TestAction.attach_volume, 'vm1', 'volume2'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.create_volume_backup, 'volume2', 'volume2-backup3'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.detach_volume, 'volume2'],
		[TestAction.create_image_from_volume, 'vm3', 'vm3-image3'],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.use_vm_backup, 'vm1-backup1'],
])




'''
The final status:
Running:['vm2', 'vm3']
Stopped:['vm1']
Enadbled:['vm1-backup1', 'volume2-backup2', 'volume2-backup3', 'image2', 'vm3-image3']
attached:[]
Detached:['volume2']
Deleted:[]
Expunged:['volume1', 'image1']
Ha:['vm2']
Group:
	vm_backup1:['vm1-backup1']---vm1@
'''