import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", checking_point=1, faild_point=100000, path_list=[
		[TestAction.create_mini_vm, 'vm1', 'cluster=cluster2'],
		[TestAction.change_vm_ha, 'vm1'],
		[TestAction.create_volume, 'volume1', 'flag=scsi'],
		[TestAction.attach_volume, 'vm1', 'volume1'],
		[TestAction.create_volume_backup, 'volume1', 'volume1-backup1'],
		[TestAction.detach_volume, 'volume1'],
		[TestAction.create_mini_vm, 'vm2', 'cluster=cluster2', 'flag=thin'],
		[TestAction.create_volume, 'volume2', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.resize_data_volume, 'volume2', 5*1024*1024],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.create_volume, 'volume3', 'size=random', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.delete_volume, 'volume3'],
		[TestAction.recover_volume, 'volume3'],
		[TestAction.add_image, 'image1', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.delete_volume_backup, 'volume1-backup1'],
		[TestAction.delete_image, 'image1'],
		[TestAction.recover_image, 'image1'],
		[TestAction.delete_image, 'image1'],
		[TestAction.expunge_image, 'image1'],
		[TestAction.create_vm_backup, 'vm1', 'vm1-backup2'],
		[TestAction.create_mini_vm, 'vm3', 'cluster=cluster2'],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.create_mini_vm, 'vm4', 'cluster=cluster1'],
		[TestAction.migrate_vm, 'vm4'],
		[TestAction.attach_volume, 'vm4', 'volume2'],
		[TestAction.detach_volume, 'volume2'],
		[TestAction.create_volume, 'volume4', 'cluster=cluster2', 'flag=thin,scsi'],
		[TestAction.delete_vm_backup, 'vm1-backup2'],
		[TestAction.create_mini_vm, 'vm5', 'memory=random', 'cluster=cluster1'],
		[TestAction.delete_volume, 'volume2'],
		[TestAction.expunge_volume, 'volume2'],
		[TestAction.destroy_vm, 'vm4'],
		[TestAction.recover_vm, 'vm4'],
		[TestAction.attach_volume, 'vm4', 'volume3'],
		[TestAction.start_vm, 'vm4'],
		[TestAction.create_volume_backup, 'volume3', 'volume3-backup3'],
		[TestAction.stop_vm, 'vm4'],
		[TestAction.detach_volume, 'volume3'],
		[TestAction.resize_data_volume, 'volume3', 5*1024*1024],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.delete_volume_backup, 'volume3-backup3'],
])




'''
The final status:
Running:['vm1']
Stopped:['vm2', 'vm3', 'vm4', 'vm5']
Enadbled:[]
attached:[]
Detached:['volume1', 'volume4', 'volume3']
Deleted:['volume1-backup1', 'vm1-backup2', 'volume3-backup3']
Expunged:['volume2', 'image1']
Ha:['vm1']
Group:
'''