import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", checking_point=1, faild_point=100000, path_list=[
		[TestAction.create_mini_vm, 'vm1', 'data_volume=true', 'cluster=cluster1'],
		[TestAction.create_volume_backup, 'auto-volume1', 'auto-volume1-backup1'],
		[TestAction.create_mini_vm, 'vm2', 'cluster=cluster1', 'flag=thin'],
		[TestAction.create_image_from_volume, 'vm2', 'vm2-image1'],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.create_volume, 'volume2', 'size=random', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.create_volume, 'volume3', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.delete_volume, 'volume3'],
		[TestAction.recover_volume, 'volume3'],
		[TestAction.add_image, 'image2', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.use_volume_backup, 'auto-volume1-backup1'],
		[TestAction.delete_image, 'vm2-image1'],
		[TestAction.delete_image, 'image2'],
		[TestAction.expunge_image, 'image2'],
		[TestAction.create_mini_vm, 'vm3', 'cluster=cluster2'],
		[TestAction.create_vm_backup, 'vm3', 'vm3-backup2'],
		[TestAction.destroy_vm, 'vm3'],
		[TestAction.recover_vm, 'vm3'],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.resize_data_volume, 'volume3', 5*1024*1024],
		[TestAction.attach_volume, 'vm3', 'volume3'],
		[TestAction.detach_volume, 'volume3'],
		[TestAction.create_volume, 'volume4', 'cluster=cluster2', 'flag=thick,scsi'],
		[TestAction.delete_vm_backup, 'vm3-backup2'],
		[TestAction.create_mini_vm, 'vm4', 'network=random', 'cluster=cluster2'],
		[TestAction.delete_volume, 'volume3'],
		[TestAction.expunge_volume, 'volume3'],
		[TestAction.destroy_vm, 'vm3'],
		[TestAction.recover_vm, 'vm3'],
		[TestAction.attach_volume, 'vm2', 'volume2'],
		[TestAction.start_vm, 'vm2'],
		[TestAction.create_volume_backup, 'volume2', 'volume2-backup3'],
		[TestAction.stop_vm, 'vm2'],
		[TestAction.detach_volume, 'volume2'],
		[TestAction.start_vm, 'vm3'],
		[TestAction.migrate_vm, 'vm3'],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.use_volume_backup, 'auto-volume1-backup1'],
])




'''
The final status:
Running:[]
Stopped:['vm1', 'vm2', 'vm4', 'vm3']
Enadbled:['auto-volume1-backup1', 'volume2-backup3']
attached:['auto-volume1']
Detached:['volume4', 'volume2']
Deleted:['vm3-backup2', 'vm2-image1']
Expunged:['volume3', 'image2']
Ha:[]
Group:
'''