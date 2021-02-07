import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", checking_point=1, faild_point=100000, path_list=[
		[TestAction.create_mini_vm, 'vm1', 'cluster=cluster1'],
		[TestAction.destroy_vm, 'vm1'],
		[TestAction.recover_vm, 'vm1'],
		[TestAction.create_mini_vm, 'vm2', 'cluster=cluster2'],
		[TestAction.create_volume, 'volume1', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.attach_volume, 'vm2', 'volume1'],
		[TestAction.create_volume_backup, 'volume1', 'volume1-backup1'],
		[TestAction.create_mini_vm, 'vm3', 'cluster=cluster1', 'flag=thin'],
		[TestAction.create_volume, 'volume2', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.resize_data_volume, 'volume2', 5*1024*1024],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.attach_volume, 'vm3', 'volume2'],
		[TestAction.delete_volume, 'volume2'],
		[TestAction.add_image, 'image1', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.start_vm, 'vm2'],
		[TestAction.create_vm_backup, 'vm2', 'vm2-backup2'],
		[TestAction.delete_vm_backup, 'vm2-backup2'],
		[TestAction.stop_vm, 'vm2'],
		[TestAction.delete_image, 'image1'],
		[TestAction.recover_image, 'image1'],
		[TestAction.delete_image, 'image1'],
		[TestAction.expunge_image, 'image1'],
		[TestAction.create_volume, 'volume3', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.attach_volume, 'vm1', 'volume3'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.create_volume_backup, 'volume3', 'volume3-backup4'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.create_mini_vm, 'vm4', 'data_volume=true', 'cluster=cluster1'],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.resize_volume, 'vm3', 5*1024*1024],
		[TestAction.create_volume, 'volume5', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.attach_volume, 'vm2', 'volume5'],
		[TestAction.create_volume, 'volume6', 'cluster=cluster2', 'flag=thick,scsi'],
		[TestAction.create_volume, 'volume7', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.attach_volume, 'vm3', 'volume7'],
		[TestAction.create_volume_backup, 'volume7', 'volume7-backup5'],
		[TestAction.stop_vm, 'vm3'],
		[TestAction.use_volume_backup, 'volume7-backup5'],
		[TestAction.start_vm, 'vm3'],
		[TestAction.start_vm, 'vm2'],
		[TestAction.delete_volume, 'volume5'],
		[TestAction.expunge_volume, 'volume5'],
		[TestAction.destroy_vm, 'vm2'],
		[TestAction.create_vm_backup, 'vm3', 'vm3-backup6'],
		[TestAction.create_mini_vm, 'vm5', 'cluster=cluster2'],
		[TestAction.migrate_vm, 'vm5'],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.use_vm_backup, 'vm3-backup6'],
])




'''
The final status:
Running:['vm5']
Stopped:['vm4', 'vm1', 'vm3']
Enadbled:['volume1-backup1', 'volume3-backup4', 'volume7-backup5', 'vm3-backup6', 'volume7-backup6']
attached:['volume3', 'auto-volume4', 'volume7']
Detached:['volume6', 'volume1']
Deleted:['vm2', 'volume2', 'vm2-backup2', 'volume1-backup2']
Expunged:['volume5', 'image1']
Ha:[]
Group:
	vm_backup1:['vm3-backup6', 'volume7-backup6']---vm3@volume7
'''