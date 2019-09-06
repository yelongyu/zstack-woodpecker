import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", checking_point=1, faild_point=100000, path_list=[
		[TestAction.create_mini_vm, 'vm1', 'cluster=cluster2'],
		[TestAction.create_volume, 'volume1', 'flag=scsi'],
		[TestAction.attach_volume, 'vm1', 'volume1'],
		[TestAction.create_volume_backup, 'volume1', 'volume1-backup1'],
		[TestAction.detach_volume, 'volume1'],
		[TestAction.create_mini_vm, 'vm2', 'memory=random', 'cluster=cluster2'],
		[TestAction.migrate_vm, 'vm1'],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.create_volume, 'volume2', 'size=random', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.create_volume, 'volume3', 'cluster=cluster1', 'flag=thin,scsi'],
		[TestAction.add_image, 'image1', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.create_vm_backup, 'vm2', 'vm2-backup2'],
		[TestAction.delete_vm_backup, 'vm2-backup2'],
		[TestAction.delete_image, 'image1'],
		[TestAction.expunge_image, 'image1'],
		[TestAction.attach_volume, 'vm2', 'volume3'],
		[TestAction.create_volume_backup, 'volume3', 'volume3-backup3'],
		[TestAction.detach_volume, 'volume3'],
		[TestAction.create_mini_vm, 'vm3', 'cluster=cluster1'],
		[TestAction.destroy_vm, 'vm3'],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.resize_volume, 'vm2', 5*1024*1024],
		[TestAction.attach_volume, 'vm1', 'volume2'],
		[TestAction.create_volume, 'volume4', 'cluster=cluster2', 'flag=thin,scsi'],
		[TestAction.create_vm_backup, 'vm1', 'vm1-backup4'],
		[TestAction.delete_vm_backup, 'vm1-backup4'],
		[TestAction.create_mini_vm, 'vm4', 'cluster=cluster2'],
		[TestAction.start_vm, 'vm4'],
		[TestAction.delete_volume, 'volume2'],
		[TestAction.expunge_volume, 'volume2'],
		[TestAction.change_vm_ha, 'vm4'],
		[TestAction.create_mini_vm, 'vm5', 'cluster=cluster1'],
		[TestAction.create_vm_backup, 'vm5', 'vm5-backup6'],
		[TestAction.resize_data_volume, 'volume4', 5*1024*1024],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.delete_vm_backup, 'vm5-backup6'],
])




'''
The final status:
Running:['vm4', 'vm5']
Stopped:['vm1', 'vm2']
Enadbled:['volume1-backup1', 'volume3-backup3']
attached:[]
Detached:['volume1', 'volume3', 'volume4']
Deleted:['vm3', 'vm2-backup2', 'vm1-backup4', 'volume2-backup4', 'vm5-backup6']
Expunged:['volume2', 'image1']
Ha:['vm4']
Group:
'''