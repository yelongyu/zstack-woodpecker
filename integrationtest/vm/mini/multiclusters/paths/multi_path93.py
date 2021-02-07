import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", checking_point=1, faild_point=100000, path_list=[
		[TestAction.add_image, 'image1', 'root', os.environ.get('isoForVmUrl')],
		[TestAction.create_vm_by_image, 'image1', 'iso', 'vm1', 'cluster=cluster2'],
		[TestAction.create_mini_vm, 'vm2', 'cluster=cluster1'],
		[TestAction.create_volume, 'volume1', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.attach_volume, 'vm2', 'volume1'],
		[TestAction.create_volume_backup, 'volume1', 'volume1-backup1'],
		[TestAction.create_mini_vm, 'vm3', 'memory=random', 'cluster=cluster1'],
		[TestAction.resize_volume, 'vm1', 5*1024*1024],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.create_volume, 'volume2', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.attach_volume, 'vm1', 'volume2'],
		[TestAction.delete_volume, 'volume1'],
		[TestAction.add_image, 'image2', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.start_vm, 'vm3'],
		[TestAction.create_vm_backup, 'vm3', 'vm3-backup2'],
		[TestAction.stop_vm, 'vm3'],
		[TestAction.use_vm_backup, 'vm3-backup2'],
		[TestAction.delete_image, 'image2'],
		[TestAction.recover_image, 'image2'],
		[TestAction.delete_image, 'image1'],
		[TestAction.expunge_image, 'image1'],
		[TestAction.create_vm_backup, 'vm1', 'vm1-backup3'],
		[TestAction.add_image, 'image3', 'root', os.environ.get('isoForVmUrl')],
		[TestAction.create_vm_by_image, 'image3', 'iso', 'vm4', 'cluster=cluster1'],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.resize_volume, 'vm1', 5*1024*1024],
		[TestAction.detach_volume, 'volume2'],
		[TestAction.create_volume, 'volume3', 'cluster=cluster1', 'flag=thick,scsi'],
		[TestAction.delete_vm_backup, 'vm1-backup3'],
		[TestAction.destroy_vm, 'vm1'],
		[TestAction.expunge_vm, 'vm1'],
		[TestAction.delete_volume, 'volume3'],
		[TestAction.expunge_volume, 'volume3'],
		[TestAction.create_mini_vm, 'vm5', 'cluster=cluster2'],
		[TestAction.destroy_vm, 'vm5'],
		[TestAction.recover_vm, 'vm5'],
		[TestAction.create_volume, 'volume4', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.attach_volume, 'vm3', 'volume4'],
		[TestAction.start_vm, 'vm3'],
		[TestAction.create_volume_backup, 'volume4', 'volume4-backup5'],
		[TestAction.stop_vm, 'vm3'],
		[TestAction.resize_data_volume, 'volume2', 5*1024*1024],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.use_vm_backup, 'vm3-backup2'],
])




'''
The final status:
Running:[]
Stopped:['vm3', 'vm5', 'vm2', 'vm4']
Enadbled:['volume1-backup1', 'vm3-backup2', 'volume4-backup5', 'image2', 'image3']
attached:['volume4']
Detached:['volume2']
Deleted:['volume1', 'vm1-backup3', 'volume2-backup3']
Expunged:['vm1', 'volume3', 'image1']
Ha:[]
Group:
	vm_backup1:['vm3-backup2']---vm3@
'''