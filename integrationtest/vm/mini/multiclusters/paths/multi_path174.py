import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", checking_point=1, faild_point=100000, path_list=[
		[TestAction.create_mini_vm, 'vm1', 'cluster=cluster1'],
		[TestAction.destroy_vm, 'vm1'],
		[TestAction.recover_vm, 'vm1'],
		[TestAction.create_volume, 'volume1', 'flag=scsi'],
		[TestAction.attach_volume, 'vm1', 'volume1'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.create_volume_backup, 'volume1', 'volume1-backup1'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.detach_volume, 'volume1'],
		[TestAction.create_mini_vm, 'vm2', 'cluster=cluster1', 'flag=thick'],
		[TestAction.create_mini_vm, 'vm3', 'cluster=cluster2'],
		[TestAction.migrate_vm, 'vm3'],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.create_volume, 'volume2', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.attach_volume, 'vm2', 'volume2'],
		[TestAction.delete_volume, 'volume2'],
		[TestAction.recover_volume, 'volume2'],
		[TestAction.add_image, 'image1', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.attach_volume, 'vm2', 'volume1'],
		[TestAction.stop_vm, 'vm2'],
		[TestAction.use_volume_backup, 'volume1-backup1'],
		[TestAction.start_vm, 'vm2'],
		[TestAction.detach_volume, 'volume1'],
		[TestAction.delete_image, 'image1'],
		[TestAction.recover_image, 'image1'],
		[TestAction.delete_image, 'image1'],
		[TestAction.expunge_image, 'image1'],
		[TestAction.attach_volume, 'vm3', 'volume2'],
		[TestAction.create_volume_backup, 'volume2', 'volume2-backup2'],
		[TestAction.detach_volume, 'volume2'],
		[TestAction.create_mini_vm, 'vm4', 'cluster=cluster2'],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.create_image_from_volume, 'vm3', 'vm3-image2'],
		[TestAction.create_volume, 'volume3', 'size=random', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.delete_volume, 'volume2'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.create_vm_backup, 'vm1', 'vm1-backup3'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.use_vm_backup, 'vm1-backup3'],
		[TestAction.create_mini_vm, 'vm5', 'network=random', 'cluster=cluster2'],
		[TestAction.expunge_volume, 'volume2'],
		[TestAction.create_mini_vm, 'vm6', 'cluster=cluster1'],
		[TestAction.attach_volume, 'vm5', 'volume3'],
		[TestAction.create_volume_backup, 'volume3', 'volume3-backup4'],
		[TestAction.detach_volume, 'volume3'],
		[TestAction.create_volume, 'volume4', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.resize_data_volume, 'volume4', 5*1024*1024],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.delete_vm_backup, 'vm1-backup3'],
])




'''
The final status:
Running:['vm3', 'vm2', 'vm4', 'vm5', 'vm6']
Stopped:['vm1']
Enadbled:['volume1-backup1', 'volume2-backup2', 'volume3-backup4', 'vm3-image2']
attached:[]
Detached:['volume1', 'volume3', 'volume4']
Deleted:['vm1-backup3']
Expunged:['volume2', 'image1']
Ha:[]
Group:
'''