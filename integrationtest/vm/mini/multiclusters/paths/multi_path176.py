import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", checking_point=1, faild_point=100000, path_list=[
		[TestAction.create_mini_vm, 'vm1', 'cluster=cluster1'],
		[TestAction.change_vm_ha, 'vm1'],
		[TestAction.create_vm_backup, 'vm1', 'vm1-backup1'],
		[TestAction.create_mini_vm, 'vm2', 'cluster=cluster2', 'flag=thin'],
		[TestAction.migrate_vm, 'vm2'],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.create_volume, 'volume1', 'size=random', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.create_volume, 'volume2', 'cluster=cluster2', 'flag=thin,scsi'],
		[TestAction.add_image, 'image1', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.delete_vm_backup, 'vm1-backup1'],
		[TestAction.delete_image, 'image1'],
		[TestAction.expunge_image, 'image1'],
		[TestAction.start_vm, 'vm2'],
		[TestAction.create_vm_backup, 'vm2', 'vm2-backup2'],
		[TestAction.stop_vm, 'vm2'],
		[TestAction.add_image, 'image2', 'root', os.environ.get('isoForVmUrl')],
		[TestAction.create_vm_by_image, 'image2', 'iso', 'vm3', 'cluster=cluster2'],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.migrate_vm, 'vm1'],
		[TestAction.create_volume, 'volume3', 'size=random', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.delete_volume, 'volume3'],
		[TestAction.recover_volume, 'volume3'],
		[TestAction.use_vm_backup, 'vm2-backup2'],
		[TestAction.create_mini_vm, 'vm4', 'cpu=random', 'cluster=cluster2'],
		[TestAction.delete_volume, 'volume3'],
		[TestAction.expunge_volume, 'volume3'],
		[TestAction.reboot_vm, 'vm1'],
		[TestAction.attach_volume, 'vm4', 'volume1'],
		[TestAction.create_volume_backup, 'volume1', 'volume1-backup3'],
		[TestAction.create_volume, 'volume4', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.resize_data_volume, 'volume4', 5*1024*1024],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.attach_volume, 'vm1', 'volume4'],
		[TestAction.create_volume_backup, 'volume4', 'volume4-backup4'],
		[TestAction.change_vm_ha, 'vm1'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.use_volume_backup, 'volume4-backup4'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.change_vm_ha, 'vm1'],
])




'''
The final status:
Running:['vm1']
Stopped:['vm2', 'vm3', 'vm4']
Enadbled:['vm2-backup2', 'volume1-backup3', 'volume4-backup4', 'image2']
attached:['volume1', 'volume4']
Detached:['volume2']
Deleted:['vm1-backup1']
Expunged:['volume3', 'image1']
Ha:['vm1']
Group:
	vm_backup1:['vm2-backup2']---vm2@
'''