import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", checking_point=1, faild_point=100000, path_list=[
		[TestAction.add_image, 'image1', 'root', os.environ.get('isoForVmUrl')],
		[TestAction.create_vm_by_image, 'image1', 'iso', 'vm1', 'cluster=cluster1'],
		[TestAction.create_mini_vm, 'vm2', 'cluster=cluster2'],
		[TestAction.create_volume, 'volume1', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.attach_volume, 'vm2', 'volume1'],
		[TestAction.create_volume_backup, 'volume1', 'volume1-backup1'],
		[TestAction.create_mini_vm, 'vm3', 'cluster=cluster1'],
		[TestAction.stop_vm, 'vm3'],
		[TestAction.start_vm, 'vm3'],
		[TestAction.resize_volume, 'vm3', 5*1024*1024],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.create_volume, 'volume2', 'size=random', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.create_volume, 'volume3', 'cluster=cluster1', 'flag=thick,scsi'],
		[TestAction.add_image, 'image2', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.attach_volume, 'vm1', 'volume3'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.create_volume_backup, 'volume3', 'volume3-backup2'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.delete_volume_backup, 'volume3-backup2'],
		[TestAction.delete_image, 'image2'],
		[TestAction.expunge_image, 'image2'],
		[TestAction.create_volume, 'volume4', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.attach_volume, 'vm2', 'volume4'],
		[TestAction.create_volume_backup, 'volume4', 'volume4-backup3'],
		[TestAction.create_mini_vm, 'vm4', 'data_volume=true', 'cluster=cluster2'],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.migrate_vm, 'vm4'],
		[TestAction.detach_volume, 'volume4'],
		[TestAction.delete_volume, 'volume4'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.create_vm_backup, 'vm1', 'vm1-backup4'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.use_vm_backup, 'vm1-backup4'],
		[TestAction.create_mini_vm, 'vm5', 'cluster=cluster2', 'flag=thin'],
		[TestAction.delete_volume, 'volume1'],
		[TestAction.expunge_volume, 'volume1'],
		[TestAction.create_mini_vm, 'vm6', 'data_volume=true', 'cluster=cluster2'],
		[TestAction.attach_volume, 'vm3', 'volume2'],
		[TestAction.start_vm, 'vm3'],
		[TestAction.create_volume_backup, 'volume2', 'volume2-backup6'],
		[TestAction.stop_vm, 'vm3'],
		[TestAction.create_volume, 'volume7', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.resize_data_volume, 'volume7', 5*1024*1024],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.use_vm_backup, 'vm1-backup4'],
])




'''
The final status:
Running:[]
Stopped:['vm2', 'vm6', 'vm3', 'vm5', 'vm4', 'vm1']
Enadbled:['volume1-backup1', 'volume4-backup3', 'vm1-backup4', 'volume3-backup4', 'volume2-backup6', 'image1']
attached:['volume3', 'auto-volume4', 'auto-volume6', 'volume2']
Detached:['volume7']
Deleted:['volume4', 'volume3-backup2']
Expunged:['volume1', 'image2']
Ha:[]
Group:
	vm_backup1:['vm1-backup4', 'volume3-backup4']---vm1@volume3
'''