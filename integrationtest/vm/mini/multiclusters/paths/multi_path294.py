import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", checking_point=1, faild_point=100000, path_list=[
		[TestAction.add_image, 'image1', 'root', os.environ.get('isoForVmUrl')],
		[TestAction.create_vm_by_image, 'image1', 'iso', 'vm1', 'cluster=cluster1'],
		[TestAction.create_mini_vm, 'vm2', 'cluster=cluster2'],
		[TestAction.create_vm_backup, 'vm2', 'vm2-backup1'],
		[TestAction.create_mini_vm, 'vm3', 'cluster=cluster1', 'flag=thin'],
		[TestAction.create_volume, 'volume1', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.resize_data_volume, 'volume1', 5*1024*1024],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.create_volume, 'volume2', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.attach_volume, 'vm1', 'volume2'],
		[TestAction.detach_volume, 'volume2'],
		[TestAction.delete_volume, 'volume2'],
		[TestAction.recover_volume, 'volume2'],
		[TestAction.add_image, 'image2', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.delete_vm_backup, 'vm2-backup1'],
		[TestAction.delete_image, 'image2'],
		[TestAction.delete_image, 'image1'],
		[TestAction.expunge_image, 'image1'],
		[TestAction.attach_volume, 'vm1', 'volume2'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.create_volume_backup, 'volume2', 'volume2-backup2'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.create_mini_vm, 'vm4', 'cluster=cluster2'],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.resize_data_volume, 'volume1', 5*1024*1024],
		[TestAction.detach_volume, 'volume2'],
		[TestAction.delete_volume, 'volume1'],
		[TestAction.start_vm, 'vm3'],
		[TestAction.create_vm_backup, 'vm3', 'vm3-backup3'],
		[TestAction.delete_vm_backup, 'vm3-backup3'],
		[TestAction.stop_vm, 'vm3'],
		[TestAction.create_mini_vm, 'vm5', 'memory=random', 'cluster=cluster2'],
		[TestAction.expunge_volume, 'volume1'],
		[TestAction.add_image, 'image3', 'root', os.environ.get('isoForVmUrl')],
		[TestAction.create_vm_by_image, 'image3', 'iso', 'vm6', 'cluster=cluster2'],
		[TestAction.create_vm_backup, 'vm2', 'vm2-backup4'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.migrate_vm, 'vm1'],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.start_vm, 'vm3'],
		[TestAction.create_vm_backup, 'vm3', 'vm3-backup5'],
		[TestAction.stop_vm, 'vm3'],
		[TestAction.use_vm_backup, 'vm3-backup5'],
])




'''
The final status:
Running:['vm2', 'vm4', 'vm5', 'vm6']
Stopped:['vm1', 'vm3']
Enadbled:['volume2-backup2', 'vm2-backup4', 'vm3-backup5', 'image3']
attached:[]
Detached:['volume2']
Deleted:['vm2-backup1', 'vm3-backup3', 'image2']
Expunged:['volume1', 'image1']
Ha:[]
Group:
	vm_backup2:['vm3-backup5']---vm3@
	vm_backup1:['vm2-backup4']---vm2@
'''