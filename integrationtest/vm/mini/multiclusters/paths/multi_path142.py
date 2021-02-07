import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", checking_point=1, faild_point=100000, path_list=[
		[TestAction.create_mini_vm, 'vm1', 'cluster=cluster2'],
		[TestAction.destroy_vm, 'vm1'],
		[TestAction.create_mini_vm, 'vm2', 'cluster=cluster1'],
		[TestAction.create_volume, 'volume1', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.attach_volume, 'vm2', 'volume1'],
		[TestAction.create_volume_backup, 'volume1', 'volume1-backup1'],
		[TestAction.create_mini_vm, 'vm3', 'cluster=cluster2'],
		[TestAction.stop_vm, 'vm3'],
		[TestAction.start_vm, 'vm3'],
		[TestAction.create_image_from_volume, 'vm2', 'vm2-image1'],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.create_volume, 'volume2', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.attach_volume, 'vm2', 'volume2'],
		[TestAction.create_volume, 'volume3', 'cluster=cluster2', 'flag=thin,scsi'],
		[TestAction.add_image, 'image2', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.stop_vm, 'vm2'],
		[TestAction.use_volume_backup, 'volume1-backup1'],
		[TestAction.start_vm, 'vm2'],
		[TestAction.delete_image, 'vm2-image1'],
		[TestAction.delete_image, 'image2'],
		[TestAction.expunge_image, 'image2'],
		[TestAction.start_vm, 'vm3'],
		[TestAction.create_vm_backup, 'vm3', 'vm3-backup2'],
		[TestAction.stop_vm, 'vm3'],
		[TestAction.destroy_vm, 'vm3'],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.migrate_vm, 'vm2'],
		[TestAction.detach_volume, 'volume2'],
		[TestAction.delete_volume, 'volume2'],
		[TestAction.recover_volume, 'volume2'],
		[TestAction.create_vm_backup, 'vm2', 'vm2-backup3'],
		[TestAction.delete_vm_backup, 'vm2-backup3'],
		[TestAction.expunge_vm, 'vm3'],
		[TestAction.delete_volume, 'volume3'],
		[TestAction.expunge_volume, 'volume3'],
		[TestAction.add_image, 'image3', 'root', os.environ.get('isoForVmUrl')],
		[TestAction.create_vm_by_image, 'image3', 'iso', 'vm4', 'cluster=cluster1'],
		[TestAction.attach_volume, 'vm4', 'volume2'],
		[TestAction.create_volume_backup, 'volume2', 'volume2-backup5'],
		[TestAction.create_mini_vm, 'vm5', 'cluster=cluster2'],
		[TestAction.migrate_vm, 'vm5'],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.stop_vm, 'vm4'],
		[TestAction.use_volume_backup, 'volume2-backup5'],
		[TestAction.start_vm, 'vm4'],
])




'''
The final status:
Running:['vm2', 'vm4']
Stopped:['vm5']
Enadbled:['volume1-backup1', 'vm3-backup2', 'volume2-backup5', 'image3']
attached:['volume1', 'volume2']
Detached:[]
Deleted:['vm1', 'vm2-backup3', 'volume1-backup3', 'vm2-image1']
Expunged:['vm3', 'volume3', 'image2']
Ha:[]
Group:
	vm_backup1:['vm3-backup2']---vm3@
'''