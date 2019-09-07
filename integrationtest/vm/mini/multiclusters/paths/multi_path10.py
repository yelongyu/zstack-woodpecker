import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", checking_point=1, faild_point=100000, path_list=[
		[TestAction.create_mini_vm, 'vm1', 'data_volume=true', 'cluster=cluster1'],
		[TestAction.create_mini_vm, 'vm2', 'cluster=cluster2'],
		[TestAction.create_vm_backup, 'vm2', 'vm2-backup1'],
		[TestAction.create_mini_vm, 'vm3', 'network=random', 'cluster=cluster1'],
		[TestAction.resize_volume, 'vm3', 5*1024*1024],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.create_volume, 'volume2', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.attach_volume, 'vm2', 'volume2'],
		[TestAction.detach_volume, 'volume2'],
		[TestAction.create_volume, 'volume3', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.delete_volume, 'volume3'],
		[TestAction.add_image, 'image1', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.recover_volume, 'volume3'],
		[TestAction.attach_volume, 'vm2', 'volume3'],
		[TestAction.create_volume_backup, 'volume3', 'volume3-backup2'],
		[TestAction.delete_volume_backup, 'volume3-backup2'],
		[TestAction.detach_volume, 'volume3'],
		[TestAction.delete_image, 'image1'],
		[TestAction.expunge_image, 'image1'],
		[TestAction.create_vm_backup, 'vm2', 'vm2-backup3'],
		[TestAction.add_image, 'image2', 'root', os.environ.get('isoForVmUrl')],
		[TestAction.create_vm_by_image, 'image2', 'iso', 'vm4', 'cluster=cluster2'],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.resize_volume, 'vm3', 5*1024*1024],
		[TestAction.attach_volume, 'vm3', 'volume3'],
		[TestAction.detach_volume, 'volume3'],
		[TestAction.delete_volume, 'volume3'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.create_vm_backup, 'vm1', 'vm1-backup4'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.use_vm_backup, 'vm1-backup4'],
		[TestAction.destroy_vm, 'vm3'],
		[TestAction.expunge_vm, 'vm3'],
		[TestAction.delete_volume, 'volume2'],
		[TestAction.expunge_volume, 'volume2'],
		[TestAction.change_vm_ha, 'vm1'],
		[TestAction.create_vm_backup, 'vm4', 'vm4-backup6'],
		[TestAction.create_image_from_volume, 'vm1', 'vm1-image3'],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.delete_vm_backup, 'vm1-backup4'],
])




'''
The final status:
Running:['vm1']
Stopped:['vm2', 'vm4']
Enadbled:['vm2-backup1', 'vm2-backup3', 'vm4-backup6', 'image2', 'vm1-image3']
attached:['auto-volume1']
Detached:[]
Deleted:['volume3', 'volume3-backup2', 'vm1-backup4', 'auto-volume1-backup4']
Expunged:['vm3', 'volume2', 'image1']
Ha:['vm1']
Group:
	vm_backup2:['vm2-backup3']---vm2@
	vm_backup1:['vm2-backup1']---vm2@
	vm_backup4:['vm4-backup6']---vm4@
'''