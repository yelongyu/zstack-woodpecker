import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", checking_point=1, faild_point=100000, path_list=[
		[TestAction.create_mini_vm, 'vm1', 'cluster=cluster2'],
		[TestAction.destroy_vm, 'vm1'],
		[TestAction.create_volume, 'volume1', 'flag=scsi'],
		[TestAction.create_mini_vm, 'vm2', ],
		[TestAction.attach_volume, 'vm2', 'volume1'],
		[TestAction.create_volume_backup, 'volume1', 'volume1-backup1'],
		[TestAction.detach_volume, 'volume1'],
		[TestAction.create_mini_vm, 'vm3', 'network=random', 'cluster=cluster1'],
		[TestAction.create_image_from_volume, 'vm3', 'vm3-image1'],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.create_volume, 'volume2', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.attach_volume, 'vm3', 'volume2'],
		[TestAction.detach_volume, 'volume2'],
		[TestAction.create_volume, 'volume3', 'cluster=cluster1', 'flag=thin,scsi'],
		[TestAction.add_image, 'image2', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.create_vm_backup, 'vm3', 'vm3-backup2'],
		[TestAction.stop_vm, 'vm3'],
		[TestAction.use_vm_backup, 'vm3-backup2'],
		[TestAction.start_vm, 'vm3'],
		[TestAction.delete_image, 'image2'],
		[TestAction.expunge_image, 'image2'],
		[TestAction.create_vm_backup, 'vm3', 'vm3-backup3'],
		[TestAction.create_mini_vm, 'vm4', 'cluster=cluster1'],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.start_vm, 'vm3'],
		[TestAction.migrate_vm, 'vm3'],
		[TestAction.create_volume, 'volume4', 'size=random', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.delete_volume, 'volume4'],
		[TestAction.start_vm, 'vm4'],
		[TestAction.create_vm_backup, 'vm4', 'vm4-backup4'],
		[TestAction.stop_vm, 'vm4'],
		[TestAction.use_vm_backup, 'vm4-backup4'],
		[TestAction.create_mini_vm, 'vm5', 'network=random', 'cluster=cluster1'],
		[TestAction.delete_volume, 'volume2'],
		[TestAction.expunge_volume, 'volume2'],
		[TestAction.recover_vm, 'vm1'],
		[TestAction.attach_volume, 'vm5', 'volume3'],
		[TestAction.create_volume_backup, 'volume3', 'volume3-backup5'],
		[TestAction.detach_volume, 'volume3'],
		[TestAction.create_image_from_volume, 'vm1', 'vm1-image3'],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.attach_volume, 'vm4', 'volume1'],
		[TestAction.use_volume_backup, 'volume1-backup1'],
		[TestAction.detach_volume, 'volume1'],
])




'''
The final status:
Running:['vm2', 'vm3', 'vm5']
Stopped:['vm4', 'vm1']
Enadbled:['volume1-backup1', 'vm3-backup2', 'vm3-backup3', 'vm4-backup4', 'volume3-backup5', 'vm3-image1', 'vm1-image3']
attached:[]
Detached:['volume3', 'volume1']
Deleted:['volume4']
Expunged:['volume2', 'image2']
Ha:[]
Group:
	vm_backup2:['vm3-backup3']---vm3@
	vm_backup3:['vm4-backup4']---vm4@
	vm_backup1:['vm3-backup2']---vm3@
'''