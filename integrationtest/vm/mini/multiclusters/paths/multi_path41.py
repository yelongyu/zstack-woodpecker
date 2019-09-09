import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", checking_point=1, faild_point=100000, path_list=[
		[TestAction.create_mini_vm, 'vm1', 'cluster=cluster1'],
		[TestAction.destroy_vm, 'vm1'],
		[TestAction.create_mini_vm, 'vm2', 'cluster=cluster2'],
		[TestAction.create_volume, 'volume1', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.attach_volume, 'vm2', 'volume1'],
		[TestAction.create_volume_backup, 'volume1', 'volume1-backup1'],
		[TestAction.create_mini_vm, 'vm3', 'cluster=cluster2'],
		[TestAction.stop_vm, 'vm3'],
		[TestAction.start_vm, 'vm3'],
		[TestAction.create_mini_vm, 'vm4', 'cluster=cluster1'],
		[TestAction.migrate_vm, 'vm4'],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.create_volume, 'volume2', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.attach_volume, 'vm3', 'volume2'],
		[TestAction.create_volume, 'volume3', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.delete_volume, 'volume3'],
		[TestAction.add_image, 'image1', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.start_vm, 'vm4'],
		[TestAction.create_vm_backup, 'vm4', 'vm4-backup2'],
		[TestAction.delete_vm_backup, 'vm4-backup2'],
		[TestAction.stop_vm, 'vm4'],
		[TestAction.delete_image, 'image1'],
		[TestAction.expunge_image, 'image1'],
		[TestAction.create_vm_backup, 'vm2', 'vm2-backup3'],
		[TestAction.change_vm_ha, 'vm2'],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.start_vm, 'vm4'],
		[TestAction.migrate_vm, 'vm4'],
		[TestAction.create_volume, 'volume4', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.attach_volume, 'vm4', 'volume4'],
		[TestAction.recover_volume, 'volume3'],
		[TestAction.attach_volume, 'vm4', 'volume3'],
		[TestAction.create_volume_backup, 'volume3', 'volume3-backup5'],
		[TestAction.stop_vm, 'vm4'],
		[TestAction.use_volume_backup, 'volume3-backup5'],
		[TestAction.start_vm, 'vm4'],
		[TestAction.create_mini_vm, 'vm5', 'cluster=cluster1'],
		[TestAction.stop_vm, 'vm5'],
		[TestAction.start_vm, 'vm5'],
		[TestAction.delete_volume, 'volume3'],
		[TestAction.expunge_volume, 'volume3'],
		[TestAction.create_mini_vm, 'vm6', 'cluster=cluster2'],
		[TestAction.create_volume, 'volume5', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.attach_volume, 'vm5', 'volume5'],
		[TestAction.create_volume_backup, 'volume5', 'volume5-backup6'],
		[TestAction.resize_volume, 'vm3', 5*1024*1024],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.create_volume, 'volume6', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.attach_volume, 'vm2', 'volume6'],
		[TestAction.create_volume_backup, 'volume6', 'volume6-backup7'],
		[TestAction.change_vm_ha, 'vm2'],
		[TestAction.stop_vm, 'vm2'],
		[TestAction.use_volume_backup, 'volume6-backup7'],
		[TestAction.start_vm, 'vm2'],
		[TestAction.change_vm_ha, 'vm2'],
])




'''
The final status:
Running:['vm4', 'vm5', 'vm2']
Stopped:['vm3', 'vm6']
Enadbled:['volume1-backup1', 'vm2-backup3', 'volume1-backup3', 'volume3-backup5', 'volume5-backup6', 'volume6-backup7']
attached:['volume1', 'volume2', 'volume4', 'volume5', 'volume6']
Detached:[]
Deleted:['vm1', 'vm4-backup2']
Expunged:['volume3', 'image1']
Ha:['vm2']
Group:
	vm_backup1:['vm2-backup3', 'volume1-backup3']---vm2@volume1
'''