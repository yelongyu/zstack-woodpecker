import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", checking_point=1, faild_point=100000, path_list=[
		[TestAction.add_image, 'image1', 'root', os.environ.get('isoForVmUrl')],
		[TestAction.create_vm_by_image, 'image1', 'iso', 'vm1', 'cluster=cluster2'],
		[TestAction.create_mini_vm, 'vm2', 'cluster=cluster1'],
		[TestAction.create_vm_backup, 'vm2', 'vm2-backup1'],
		[TestAction.destroy_vm, 'vm1'],
		[TestAction.expunge_vm, 'vm1'],
		[TestAction.create_mini_vm, 'vm3', 'cluster=cluster2'],
		[TestAction.migrate_vm, 'vm3'],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.create_volume, 'volume1', 'size=random', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.create_volume, 'volume2', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.delete_volume, 'volume2'],
		[TestAction.recover_volume, 'volume2'],
		[TestAction.add_image, 'image2', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.delete_vm_backup, 'vm2-backup1'],
		[TestAction.delete_image, 'image2'],
		[TestAction.recover_image, 'image2'],
		[TestAction.delete_image, 'image1'],
		[TestAction.expunge_image, 'image1'],
		[TestAction.start_vm, 'vm3'],
		[TestAction.create_vm_backup, 'vm3', 'vm3-backup2'],
		[TestAction.stop_vm, 'vm3'],
		[TestAction.create_mini_vm, 'vm4', 'data_volume=true', 'cluster=cluster2'],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.resize_volume, 'vm4', 5*1024*1024],
		[TestAction.attach_volume, 'vm2', 'volume2'],
		[TestAction.detach_volume, 'volume2'],
		[TestAction.delete_volume, 'volume2'],
		[TestAction.attach_volume, 'vm4', 'volume1'],
		[TestAction.create_volume_backup, 'volume1', 'volume1-backup3'],
		[TestAction.delete_volume_backup, 'volume1-backup3'],
		[TestAction.detach_volume, 'volume1'],
		[TestAction.create_mini_vm, 'vm5', 'memory=random', 'cluster=cluster1'],
		[TestAction.expunge_volume, 'volume2'],
		[TestAction.create_mini_vm, 'vm6', 'cluster=cluster1'],
		[TestAction.create_vm_backup, 'vm4', 'vm4-backup4'],
		[TestAction.migrate_vm, 'vm5'],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.use_vm_backup, 'vm4-backup4'],
])




'''
The final status:
Running:['vm5', 'vm6']
Stopped:['vm4', 'vm2', 'vm3']
Enadbled:['vm3-backup2', 'vm4-backup4', 'auto-volume4-backup4', 'image2']
attached:['auto-volume4']
Detached:['volume1']
Deleted:['vm2-backup1', 'volume1-backup3']
Expunged:['vm1', 'volume2', 'image1']
Ha:[]
Group:
	vm_backup2:['vm4-backup4', 'auto-volume4-backup4']---vm4@auto-volume4
	vm_backup1:['vm3-backup2']---vm3@
'''