import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", checking_point=1, faild_point=100000, path_list=[
		[TestAction.create_mini_vm, 'vm1', 'data_volume=true', 'cluster=cluster1'],
		[TestAction.create_volume_backup, 'auto-volume1', 'auto-volume1-backup1'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.create_mini_vm, 'vm2', 'cluster=cluster2'],
		[TestAction.migrate_vm, 'vm2'],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.create_volume, 'volume2', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.attach_volume, 'vm1', 'volume2'],
		[TestAction.detach_volume, 'volume2'],
		[TestAction.create_volume, 'volume3', 'cluster=cluster2', 'flag=thin,scsi'],
		[TestAction.add_image, 'image1', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.create_vm_backup, 'vm1', 'vm1-backup2'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.use_vm_backup, 'vm1-backup2'],
		[TestAction.delete_image, 'image1'],
		[TestAction.expunge_image, 'image1'],
		[TestAction.create_vm_backup, 'vm2', 'vm2-backup4'],
		[TestAction.create_mini_vm, 'vm3', 'cluster=cluster2'],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.resize_data_volume, 'volume3', 5*1024*1024],
		[TestAction.attach_volume, 'vm3', 'volume3'],
		[TestAction.create_volume, 'volume4', 'cluster=cluster1', 'flag=thin,scsi'],
		[TestAction.delete_volume_backup, 'auto-volume1-backup1'],
		[TestAction.create_mini_vm, 'vm4', 'cluster=cluster1', 'flag=thick'],
		[TestAction.delete_volume, 'volume4'],
		[TestAction.expunge_volume, 'volume4'],
		[TestAction.destroy_vm, 'vm4'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.create_vm_backup, 'vm1', 'vm1-backup5'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.resize_volume, 'vm1', 5*1024*1024],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.attach_volume, 'vm3', 'volume2'],
		[TestAction.start_vm, 'vm3'],
		[TestAction.create_volume_backup, 'volume2', 'volume2-backup7'],
		[TestAction.stop_vm, 'vm3'],
		[TestAction.use_volume_backup, 'volume2-backup7'],
		[TestAction.detach_volume, 'volume2'],
])




'''
The final status:
Running:[]
Stopped:['vm2', 'vm1', 'vm3']
Enadbled:['vm1-backup2', 'auto-volume1-backup2', 'vm2-backup4', 'vm1-backup5', 'auto-volume1-backup5', 'volume2-backup7']
attached:['auto-volume1', 'volume3']
Detached:['volume2']
Deleted:['vm4', 'auto-volume1-backup1']
Expunged:['volume4', 'image1']
Ha:[]
Group:
	vm_backup2:['vm2-backup4']---vm2@
	vm_backup3:['vm1-backup5', 'auto-volume1-backup5']---vm1@auto-volume1
	vm_backup1:['vm1-backup2', 'auto-volume1-backup2']---vm1@auto-volume1
'''