import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", checking_point=1, faild_point=100000, path_list=[
		[TestAction.create_mini_vm, 'vm1', 'cluster=cluster2'],
		[TestAction.destroy_vm, 'vm1'],
		[TestAction.create_volume, 'volume1', 'flag=scsi'],
		[TestAction.create_mini_vm, 'vm2', ],
		[TestAction.attach_volume, 'vm2', 'volume1'],
		[TestAction.create_volume_backup, 'volume1', 'volume1-backup1'],
		[TestAction.detach_volume, 'volume1'],
		[TestAction.create_mini_vm, 'vm3', 'cluster=cluster2'],
		[TestAction.start_vm, 'vm3'],
		[TestAction.stop_vm, 'vm3'],
		[TestAction.create_mini_vm, 'vm4', 'cluster=cluster1'],
		[TestAction.resize_volume, 'vm3', 5*1024*1024],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.create_volume, 'volume2', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.attach_volume, 'vm3', 'volume2'],
		[TestAction.detach_volume, 'volume2'],
		[TestAction.create_volume, 'volume3', 'cluster=cluster1', 'flag=thin,scsi'],
		[TestAction.add_image, 'image1', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.attach_volume, 'vm4', 'volume1'],
		[TestAction.stop_vm, 'vm4'],
		[TestAction.use_volume_backup, 'volume1-backup1'],
		[TestAction.start_vm, 'vm4'],
		[TestAction.detach_volume, 'volume1'],
		[TestAction.delete_image, 'image1'],
		[TestAction.expunge_image, 'image1'],
		[TestAction.start_vm, 'vm3'],
		[TestAction.create_vm_backup, 'vm3', 'vm3-backup2'],
		[TestAction.stop_vm, 'vm3'],
		[TestAction.destroy_vm, 'vm4'],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.start_vm, 'vm3'],
		[TestAction.migrate_vm, 'vm3'],
		[TestAction.attach_volume, 'vm3', 'volume2'],
		[TestAction.delete_volume, 'volume3'],
		[TestAction.delete_volume_backup, 'volume1-backup1'],
		[TestAction.create_mini_vm, 'vm5', 'cluster=cluster2', 'flag=thick'],
		[TestAction.delete_volume, 'volume2'],
		[TestAction.expunge_volume, 'volume2'],
		[TestAction.create_mini_vm, 'vm6', 'cluster=cluster1'],
		[TestAction.destroy_vm, 'vm6'],
		[TestAction.attach_volume, 'vm5', 'volume1'],
		[TestAction.create_volume_backup, 'volume1', 'volume1-backup3'],
		[TestAction.detach_volume, 'volume1'],
		[TestAction.create_mini_vm, 'vm7', 'cluster=cluster1'],
		[TestAction.migrate_vm, 'vm7'],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.delete_vm_backup, 'vm3-backup2'],
])




'''
The final status:
Running:['vm2', 'vm3', 'vm5']
Stopped:['vm7']
Enadbled:['volume1-backup3']
attached:[]
Detached:['volume1']
Deleted:['vm1', 'vm4', 'vm6', 'volume3', 'volume1-backup1', 'vm3-backup2']
Expunged:['volume2', 'image1']
Ha:[]
Group:
'''