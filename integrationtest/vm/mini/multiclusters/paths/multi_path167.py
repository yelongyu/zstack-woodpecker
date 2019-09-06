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
		[TestAction.create_mini_vm, 'vm2', 'memory=random', 'cluster=cluster2'],
		[TestAction.create_image_from_volume, 'vm1', 'vm1-image1'],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.create_volume, 'volume2', 'size=random', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.delete_volume, 'volume2'],
		[TestAction.recover_volume, 'volume2'],
		[TestAction.add_image, 'image2', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.create_vm_backup, 'vm2', 'vm2-backup2'],
		[TestAction.delete_vm_backup, 'vm2-backup2'],
		[TestAction.delete_image, 'vm1-image1'],
		[TestAction.expunge_image, 'vm1-image1'],
		[TestAction.attach_volume, 'vm2', 'volume2'],
		[TestAction.create_volume_backup, 'volume2', 'volume2-backup3'],
		[TestAction.detach_volume, 'volume2'],
		[TestAction.destroy_vm, 'vm2'],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.create_mini_vm, 'vm3', 'cluster=cluster1'],
		[TestAction.migrate_vm, 'vm3'],
		[TestAction.create_volume, 'volume3', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.attach_volume, 'vm1', 'volume3'],
		[TestAction.detach_volume, 'volume3'],
		[TestAction.create_volume, 'volume4', 'cluster=cluster2', 'flag=thick,scsi'],
		[TestAction.delete_volume_backup, 'volume2-backup3'],
		[TestAction.create_mini_vm, 'vm4', 'cluster=cluster1', 'flag=thin'],
		[TestAction.delete_volume, 'volume2'],
		[TestAction.expunge_volume, 'volume2'],
		[TestAction.reboot_vm, 'vm1'],
		[TestAction.create_vm_backup, 'vm1', 'vm1-backup4'],
		[TestAction.create_image_from_volume, 'vm3', 'vm3-image3'],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.create_vm_backup, 'vm3', 'vm3-backup5'],
		[TestAction.stop_vm, 'vm3'],
		[TestAction.use_vm_backup, 'vm3-backup5'],
		[TestAction.start_vm, 'vm3'],
])




'''
The final status:
Running:['vm1', 'vm4', 'vm3']
Stopped:[]
Enadbled:['volume1-backup1', 'vm1-backup4', 'vm3-backup5', 'image2', 'vm3-image3']
attached:[]
Detached:['volume1', 'volume3', 'volume4']
Deleted:['vm2', 'vm2-backup2', 'volume2-backup3']
Expunged:['volume2', 'vm1-image1']
Ha:['vm1']
Group:
	vm_backup2:['vm3-backup5']---vm3@
	vm_backup1:['vm1-backup4']---vm1@
'''