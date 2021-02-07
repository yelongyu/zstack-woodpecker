import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", checking_point=1, faild_point=100000, path_list=[
		[TestAction.create_mini_vm, 'vm1', 'cluster=cluster2'],
		[TestAction.change_vm_ha, 'vm1'],
		[TestAction.create_mini_vm, 'vm2', 'cluster=cluster1'],
		[TestAction.create_vm_backup, 'vm2', 'vm2-backup1'],
		[TestAction.destroy_vm, 'vm1'],
		[TestAction.expunge_vm, 'vm1'],
		[TestAction.migrate_vm, 'vm2'],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.create_volume, 'volume1', 'size=random', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.create_volume, 'volume2', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.delete_volume, 'volume2'],
		[TestAction.add_image, 'image1', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.attach_volume, 'vm2', 'volume1'],
		[TestAction.start_vm, 'vm2'],
		[TestAction.create_volume_backup, 'volume1', 'volume1-backup2'],
		[TestAction.stop_vm, 'vm2'],
		[TestAction.delete_volume_backup, 'volume1-backup2'],
		[TestAction.delete_image, 'image1'],
		[TestAction.expunge_image, 'image1'],
		[TestAction.create_mini_vm, 'vm3', 'cluster=cluster2'],
		[TestAction.create_volume, 'volume3', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.attach_volume, 'vm3', 'volume3'],
		[TestAction.create_volume_backup, 'volume3', 'volume3-backup3'],
		[TestAction.start_vm, 'vm2'],
		[TestAction.reboot_vm, 'vm2'],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.resize_data_volume, 'volume3', 5*1024*1024],
		[TestAction.create_volume, 'volume4', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.attach_volume, 'vm2', 'volume4'],
		[TestAction.delete_volume, 'volume3'],
		[TestAction.recover_volume, 'volume3'],
		[TestAction.use_volume_backup, 'volume3-backup3'],
		[TestAction.create_mini_vm, 'vm4', 'cluster=cluster2', 'flag=thick'],
		[TestAction.delete_volume, 'volume3'],
		[TestAction.expunge_volume, 'volume3'],
		[TestAction.create_mini_vm, 'vm5', 'cluster=cluster1'],
		[TestAction.create_vm_backup, 'vm4', 'vm4-backup4'],
		[TestAction.resize_volume, 'vm4', 5*1024*1024],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.create_volume, 'volume5', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.attach_volume, 'vm5', 'volume5'],
		[TestAction.create_volume_backup, 'volume5', 'volume5-backup5'],
		[TestAction.delete_volume_backup, 'volume5-backup5'],
])




'''
The final status:
Running:['vm2', 'vm5']
Stopped:['vm3', 'vm4']
Enadbled:['vm2-backup1', 'volume3-backup3', 'vm4-backup4']
attached:['volume1', 'volume4', 'volume5']
Detached:[]
Deleted:['volume2', 'volume1-backup2', 'volume5-backup5']
Expunged:['vm1', 'volume3', 'image1']
Ha:[]
Group:
	vm_backup2:['vm4-backup4']---vm4@
	vm_backup1:['vm2-backup1']---vm2@
'''