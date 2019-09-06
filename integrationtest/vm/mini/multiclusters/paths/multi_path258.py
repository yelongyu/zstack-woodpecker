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
		[TestAction.migrate_vm, 'vm2'],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.create_mini_vm, 'vm3', 'cluster=cluster2'],
		[TestAction.create_volume, 'volume2', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.attach_volume, 'vm3', 'volume2'],
		[TestAction.create_volume, 'volume3', 'cluster=cluster1', 'flag=thin,scsi'],
		[TestAction.add_image, 'image2', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.create_vm_backup, 'vm2', 'vm2-backup2'],
		[TestAction.stop_vm, 'vm2'],
		[TestAction.use_vm_backup, 'vm2-backup2'],
		[TestAction.start_vm, 'vm2'],
		[TestAction.delete_image, 'image2'],
		[TestAction.recover_image, 'image2'],
		[TestAction.delete_image, 'image2'],
		[TestAction.expunge_image, 'image2'],
		[TestAction.create_vm_backup, 'vm3', 'vm3-backup3'],
		[TestAction.destroy_vm, 'vm3'],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.create_mini_vm, 'vm4', 'cluster=cluster2'],
		[TestAction.resize_volume, 'vm1', 5*1024*1024],
		[TestAction.create_volume, 'volume4', 'size=random', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.create_volume, 'volume5', 'cluster=cluster2', 'flag=thick,scsi'],
		[TestAction.delete_vm_backup, 'vm2-backup2'],
		[TestAction.start_vm, 'vm4'],
		[TestAction.stop_vm, 'vm4'],
		[TestAction.delete_volume, 'volume4'],
		[TestAction.expunge_volume, 'volume4'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.reboot_vm, 'vm1'],
		[TestAction.attach_volume, 'vm1', 'volume1'],
		[TestAction.create_volume_backup, 'volume1', 'volume1-backup5'],
		[TestAction.detach_volume, 'volume1'],
		[TestAction.resize_data_volume, 'volume5', 5*1024*1024],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.delete_volume_backup, 'volume1-backup1'],
])




'''
The final status:
Running:['vm1']
Stopped:['vm2', 'vm4']
Enadbled:['vm3-backup3', 'volume2-backup3', 'volume1-backup5', 'image1']
attached:[]
Detached:['volume3', 'volume2', 'volume5', 'volume1']
Deleted:['vm3', 'vm2-backup2', 'volume1-backup1']
Expunged:['volume4', 'image2']
Ha:[]
Group:
	vm_backup2:['vm3-backup3', 'volume2-backup3']---vm3@volume2
'''