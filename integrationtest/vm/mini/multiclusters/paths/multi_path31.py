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
		[TestAction.create_mini_vm, 'vm3', 'cluster=cluster1'],
		[TestAction.stop_vm, 'vm3'],
		[TestAction.start_vm, 'vm3'],
		[TestAction.create_mini_vm, 'vm4', 'cluster=cluster2'],
		[TestAction.resize_volume, 'vm3', 5*1024*1024],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.create_volume, 'volume2', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.attach_volume, 'vm3', 'volume2'],
		[TestAction.delete_volume, 'volume2'],
		[TestAction.add_image, 'image1', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.attach_volume, 'vm2', 'volume1'],
		[TestAction.stop_vm, 'vm2'],
		[TestAction.use_volume_backup, 'volume1-backup1'],
		[TestAction.start_vm, 'vm2'],
		[TestAction.detach_volume, 'volume1'],
		[TestAction.delete_image, 'image1'],
		[TestAction.expunge_image, 'image1'],
		[TestAction.attach_volume, 'vm4', 'volume1'],
		[TestAction.start_vm, 'vm4'],
		[TestAction.create_volume_backup, 'volume1', 'volume1-backup2'],
		[TestAction.stop_vm, 'vm4'],
		[TestAction.detach_volume, 'volume1'],
		[TestAction.add_image, 'image2', 'root', os.environ.get('isoForVmUrl')],
		[TestAction.create_vm_by_image, 'image2', 'iso', 'vm5', 'cluster=cluster2'],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.resize_volume, 'vm2', 5*1024*1024],
		[TestAction.create_volume, 'volume3', 'size=random', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.create_volume, 'volume4', 'cluster=cluster2', 'flag=thin,scsi'],
		[TestAction.delete_volume_backup, 'volume1-backup1'],
		[TestAction.create_mini_vm, 'vm6', 'memory=random', 'cluster=cluster2'],
		[TestAction.delete_volume, 'volume4'],
		[TestAction.expunge_volume, 'volume4'],
		[TestAction.create_mini_vm, 'vm7', 'cluster=cluster1'],
		[TestAction.create_vm_backup, 'vm7', 'vm7-backup3'],
		[TestAction.migrate_vm, 'vm7'],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.attach_volume, 'vm6', 'volume1'],
		[TestAction.use_volume_backup, 'volume1-backup2'],
		[TestAction.detach_volume, 'volume1'],
])




'''
The final status:
Running:['vm2', 'vm7']
Stopped:['vm4', 'vm3', 'vm5', 'vm6']
Enadbled:['volume1-backup2', 'vm7-backup3', 'image2']
attached:[]
Detached:['volume3', 'volume1']
Deleted:['vm1', 'volume2', 'volume1-backup1']
Expunged:['volume4', 'image1']
Ha:[]
Group:
	vm_backup1:['vm7-backup3']---vm7@
'''