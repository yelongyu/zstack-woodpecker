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
		[TestAction.create_mini_vm, 'vm2', 'cluster=cluster1'],
		[TestAction.destroy_vm, 'vm2'],
		[TestAction.expunge_vm, 'vm2'],
		[TestAction.resize_volume, 'vm1', 5*1024*1024],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.create_volume, 'volume2', 'size=random', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.delete_volume, 'volume2'],
		[TestAction.add_image, 'image1', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.attach_volume, 'vm1', 'volume1'],
		[TestAction.change_vm_ha, 'vm1'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.use_volume_backup, 'volume1-backup1'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.change_vm_ha, 'vm1'],
		[TestAction.detach_volume, 'volume1'],
		[TestAction.delete_image, 'image1'],
		[TestAction.recover_image, 'image1'],
		[TestAction.delete_image, 'image1'],
		[TestAction.expunge_image, 'image1'],
		[TestAction.create_vm_backup, 'vm1', 'vm1-backup2'],
		[TestAction.create_mini_vm, 'vm3', 'data_volume=true', 'cluster=cluster1'],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.create_volume, 'volume4', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.resize_data_volume, 'volume4', 5*1024*1024],
		[TestAction.create_volume, 'volume5', 'size=random', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.delete_volume, 'volume5'],
		[TestAction.recover_volume, 'volume5'],
		[TestAction.delete_vm_backup, 'vm1-backup2'],
		[TestAction.destroy_vm, 'vm3'],
		[TestAction.expunge_vm, 'vm3'],
		[TestAction.delete_volume, 'volume5'],
		[TestAction.expunge_volume, 'volume5'],
		[TestAction.create_mini_vm, 'vm4', 'cluster=cluster1'],
		[TestAction.change_vm_ha, 'vm4'],
		[TestAction.attach_volume, 'vm4', 'volume4'],
		[TestAction.create_volume_backup, 'volume4', 'volume4-backup3'],
		[TestAction.detach_volume, 'volume4'],
		[TestAction.resize_volume, 'vm1', 5*1024*1024],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.create_mini_vm, 'vm5', ],
		[TestAction.create_vm_backup, 'vm5', 'vm5-backup4'],
		[TestAction.stop_vm, 'vm5'],
		[TestAction.use_vm_backup, 'vm5-backup4'],
])




'''
The final status:
Running:['vm1', 'vm4']
Stopped:['vm5']
Enadbled:['volume1-backup1', 'volume4-backup3', 'vm5-backup4']
attached:[]
Detached:['volume1', 'auto-volume3', 'volume4']
Deleted:['volume2', 'vm1-backup2']
Expunged:['vm2', 'vm3', 'volume5', 'image1']
Ha:['vm1', 'vm4']
Group:
	vm_backup1:['vm5-backup4']---vm5@
'''