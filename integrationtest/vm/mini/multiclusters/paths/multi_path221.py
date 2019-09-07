import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", checking_point=1, faild_point=100000, path_list=[
		[TestAction.create_mini_vm, 'vm1', 'cluster=cluster2'],
		[TestAction.destroy_vm, 'vm1'],
		[TestAction.recover_vm, 'vm1'],
		[TestAction.create_volume, 'volume1', 'flag=scsi'],
		[TestAction.attach_volume, 'vm1', 'volume1'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.create_volume_backup, 'volume1', 'volume1-backup1'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.detach_volume, 'volume1'],
		[TestAction.create_mini_vm, 'vm2', 'memory=random', 'cluster=cluster2'],
		[TestAction.create_mini_vm, 'vm3', 'cluster=cluster1'],
		[TestAction.migrate_vm, 'vm3'],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.create_volume, 'volume2', 'size=random', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.create_volume, 'volume3', 'cluster=cluster2', 'flag=thick,scsi'],
		[TestAction.add_image, 'image1', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.delete_volume_backup, 'volume1-backup1'],
		[TestAction.delete_image, 'image1'],
		[TestAction.recover_image, 'image1'],
		[TestAction.delete_image, 'image1'],
		[TestAction.expunge_image, 'image1'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.create_vm_backup, 'vm1', 'vm1-backup2'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.add_image, 'image2', 'root', os.environ.get('isoForVmUrl')],
		[TestAction.create_vm_by_image, 'image2', 'iso', 'vm4', 'cluster=cluster2'],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.resize_volume, 'vm1', 5*1024*1024],
		[TestAction.attach_volume, 'vm3', 'volume2'],
		[TestAction.create_volume, 'volume4', 'cluster=cluster2', 'flag=thick,scsi'],
		[TestAction.use_vm_backup, 'vm1-backup2'],
		[TestAction.destroy_vm, 'vm2'],
		[TestAction.expunge_vm, 'vm2'],
		[TestAction.delete_volume, 'volume3'],
		[TestAction.expunge_volume, 'volume3'],
		[TestAction.create_mini_vm, 'vm5', 'data_volume=true', 'cluster=cluster1'],
		[TestAction.attach_volume, 'vm3', 'volume4'],
		[TestAction.start_vm, 'vm3'],
		[TestAction.create_volume_backup, 'volume4', 'volume4-backup3'],
		[TestAction.stop_vm, 'vm3'],
		[TestAction.detach_volume, 'volume4'],
		[TestAction.resize_data_volume, 'volume4', 5*1024*1024],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.attach_volume, 'vm5', 'volume4'],
		[TestAction.stop_vm, 'vm5'],
		[TestAction.use_volume_backup, 'volume4-backup3'],
		[TestAction.start_vm, 'vm5'],
		[TestAction.detach_volume, 'volume4'],
])




'''
The final status:
Running:['vm5']
Stopped:['vm1', 'vm3', 'vm4']
Enadbled:['vm1-backup2', 'volume4-backup3', 'image2']
attached:['volume2', 'auto-volume5']
Detached:['volume1', 'volume4']
Deleted:['volume1-backup1']
Expunged:['vm2', 'volume3', 'image1']
Ha:[]
Group:
	vm_backup1:['vm1-backup2']---vm1@
'''