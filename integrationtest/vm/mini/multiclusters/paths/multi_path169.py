import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", checking_point=1, faild_point=100000, path_list=[
		[TestAction.create_mini_vm, 'vm1', 'cluster=cluster1'],
		[TestAction.create_mini_vm, 'vm2', 'cluster=cluster2'],
		[TestAction.create_volume, 'volume1', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.attach_volume, 'vm2', 'volume1'],
		[TestAction.create_volume_backup, 'volume1', 'volume1-backup1'],
		[TestAction.create_mini_vm, 'vm3', 'cluster=cluster2', 'flag=thin'],
		[TestAction.migrate_vm, 'vm3'],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.create_volume, 'volume2', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.attach_volume, 'vm1', 'volume2'],
		[TestAction.create_volume, 'volume3', 'cluster=cluster1', 'flag=thin,scsi'],
		[TestAction.add_image, 'image1', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.start_vm, 'vm3'],
		[TestAction.create_vm_backup, 'vm3', 'vm3-backup2'],
		[TestAction.stop_vm, 'vm3'],
		[TestAction.use_vm_backup, 'vm3-backup2'],
		[TestAction.delete_image, 'image1'],
		[TestAction.expunge_image, 'image1'],
		[TestAction.create_vm_backup, 'vm1', 'vm1-backup3'],
		[TestAction.add_image, 'image2', 'root', os.environ.get('isoForVmUrl')],
		[TestAction.create_vm_by_image, 'image2', 'iso', 'vm4', 'cluster=cluster1'],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.resize_data_volume, 'volume3', 5*1024*1024],
		[TestAction.attach_volume, 'vm4', 'volume3'],
		[TestAction.delete_volume, 'volume3'],
		[TestAction.recover_volume, 'volume3'],
		[TestAction.delete_vm_backup, 'vm1-backup3'],
		[TestAction.create_mini_vm, 'vm5', 'memory=random', 'cluster=cluster2'],
		[TestAction.delete_volume, 'volume2'],
		[TestAction.expunge_volume, 'volume2'],
		[TestAction.destroy_vm, 'vm1'],
		[TestAction.attach_volume, 'vm4', 'volume3'],
		[TestAction.start_vm, 'vm4'],
		[TestAction.create_volume_backup, 'volume3', 'volume3-backup5'],
		[TestAction.stop_vm, 'vm4'],
		[TestAction.start_vm, 'vm4'],
		[TestAction.migrate_vm, 'vm4'],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.delete_volume_backup, 'volume3-backup5'],
])




'''
The final status:
Running:['vm4']
Stopped:['vm2', 'vm3', 'vm5']
Enadbled:['volume1-backup1', 'vm3-backup2', 'image2']
attached:['volume1', 'volume3']
Detached:[]
Deleted:['vm1', 'vm1-backup3', 'volume2-backup3', 'volume3-backup5']
Expunged:['volume2', 'image1']
Ha:[]
Group:
	vm_backup1:['vm3-backup2']---vm3@
'''