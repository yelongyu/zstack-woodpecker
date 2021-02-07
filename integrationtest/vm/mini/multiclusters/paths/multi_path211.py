import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", checking_point=1, faild_point=100000, path_list=[
		[TestAction.create_mini_vm, 'vm1', 'cluster=cluster1'],
		[TestAction.destroy_vm, 'vm1'],
		[TestAction.create_mini_vm, 'vm2', 'cluster=cluster2'],
		[TestAction.create_vm_backup, 'vm2', 'vm2-backup1'],
		[TestAction.create_mini_vm, 'vm3', 'cluster=cluster1', 'flag=thick'],
		[TestAction.resize_volume, 'vm3', 5*1024*1024],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.create_volume, 'volume1', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.attach_volume, 'vm3', 'volume1'],
		[TestAction.delete_volume, 'volume1'],
		[TestAction.recover_volume, 'volume1'],
		[TestAction.add_image, 'image1', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.attach_volume, 'vm3', 'volume1'],
		[TestAction.create_volume_backup, 'volume1', 'volume1-backup2'],
		[TestAction.stop_vm, 'vm3'],
		[TestAction.use_volume_backup, 'volume1-backup2'],
		[TestAction.start_vm, 'vm3'],
		[TestAction.delete_image, 'image1'],
		[TestAction.recover_image, 'image1'],
		[TestAction.delete_image, 'image1'],
		[TestAction.expunge_image, 'image1'],
		[TestAction.create_vm_backup, 'vm3', 'vm3-backup3'],
		[TestAction.change_vm_ha, 'vm3'],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.start_vm, 'vm2'],
		[TestAction.migrate_vm, 'vm2'],
		[TestAction.create_volume, 'volume2', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.attach_volume, 'vm2', 'volume2'],
		[TestAction.create_volume, 'volume3', 'cluster=cluster2', 'flag=thick,scsi'],
		[TestAction.create_volume, 'volume4', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.attach_volume, 'vm3', 'volume4'],
		[TestAction.create_volume_backup, 'volume4', 'volume4-backup5'],
		[TestAction.delete_volume_backup, 'volume4-backup5'],
		[TestAction.create_mini_vm, 'vm4', 'cluster=cluster2', 'flag=thin'],
		[TestAction.delete_volume, 'volume2'],
		[TestAction.expunge_volume, 'volume2'],
		[TestAction.destroy_vm, 'vm3'],
		[TestAction.create_mini_vm, 'vm5', 'cluster=cluster1'],
		[TestAction.attach_volume, 'vm5', 'volume4'],
		[TestAction.create_volume_backup, 'volume4', 'volume4-backup6'],
		[TestAction.resize_data_volume, 'volume3', 5*1024*1024],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.start_vm, 'vm5'],
		[TestAction.create_vm_backup, 'vm5', 'vm5-backup7'],
		[TestAction.stop_vm, 'vm5'],
		[TestAction.use_vm_backup, 'vm5-backup7'],
])




'''
The final status:
Running:['vm2', 'vm4']
Stopped:['vm5']
Enadbled:['vm2-backup1', 'volume1-backup2', 'vm3-backup3', 'volume1-backup3', 'volume4-backup6', 'vm5-backup7', 'volume4-backup7']
attached:['volume4']
Detached:['volume3', 'volume1']
Deleted:['vm1', 'vm3', 'volume4-backup5']
Expunged:['volume2', 'image1']
Ha:[]
Group:
	vm_backup2:['vm3-backup3', 'volume1-backup3']---vm3@volume1
	vm_backup3:['vm5-backup7', 'volume4-backup7']---vm5@volume4
	vm_backup1:['vm2-backup1']---vm2@
'''