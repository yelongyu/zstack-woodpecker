import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", checking_point=1, faild_point=100000, path_list=[
		[TestAction.add_image, 'image1', 'root', os.environ.get('isoForVmUrl')],
		[TestAction.create_vm_by_image, 'image1', 'iso', 'vm1', 'cluster=cluster1'],
		[TestAction.create_volume, 'volume1', 'flag=scsi'],
		[TestAction.attach_volume, 'vm1', 'volume1'],
		[TestAction.create_volume_backup, 'volume1', 'volume1-backup1'],
		[TestAction.detach_volume, 'volume1'],
		[TestAction.create_mini_vm, 'vm2', 'cluster=cluster1'],
		[TestAction.start_vm, 'vm2'],
		[TestAction.resize_volume, 'vm1', 5*1024*1024],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.create_volume, 'volume2', 'size=random', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.create_volume, 'volume3', 'cluster=cluster1', 'flag=thick,scsi'],
		[TestAction.add_image, 'image2', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.delete_volume_backup, 'volume1-backup1'],
		[TestAction.delete_image, 'image1'],
		[TestAction.expunge_image, 'image1'],
		[TestAction.attach_volume, 'vm1', 'volume2'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.create_volume_backup, 'volume2', 'volume2-backup2'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.detach_volume, 'volume2'],
		[TestAction.create_mini_vm, 'vm3', 'data_volume=true', 'cluster=cluster2'],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.migrate_vm, 'vm3'],
		[TestAction.create_volume, 'volume5', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.attach_volume, 'vm3', 'volume5'],
		[TestAction.detach_volume, 'volume5'],
		[TestAction.delete_volume, 'volume5'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.create_vm_backup, 'vm1', 'vm1-backup3'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.use_vm_backup, 'vm1-backup3'],
		[TestAction.create_mini_vm, 'vm4', 'cluster=cluster2', 'flag=thin'],
		[TestAction.expunge_volume, 'volume5'],
		[TestAction.create_mini_vm, 'vm5', 'data_volume=true', 'cluster=cluster2'],
		[TestAction.create_volume_backup, 'auto-volume3', 'auto-volume3-backup4'],
		[TestAction.create_volume, 'volume7', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.resize_data_volume, 'volume7', 5*1024*1024],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.use_vm_backup, 'vm1-backup3'],
])




'''
The final status:
Running:[]
Stopped:['vm2', 'vm5', 'vm1', 'vm3', 'vm4']
Enadbled:['volume2-backup2', 'vm1-backup3', 'auto-volume3-backup4', 'image2']
attached:['auto-volume3', 'auto-volume5']
Detached:['volume1', 'volume3', 'volume2', 'volume7']
Deleted:['volume1-backup1']
Expunged:['volume5', 'image1']
Ha:[]
Group:
	vm_backup1:['vm1-backup3']---vm1@
'''