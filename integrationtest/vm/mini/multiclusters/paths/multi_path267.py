import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", checking_point=1, faild_point=100000, path_list=[
		[TestAction.create_mini_vm, 'vm1', 'cluster=cluster2'],
		[TestAction.change_vm_ha, 'vm1'],
		[TestAction.create_vm_backup, 'vm1', 'vm1-backup1'],
		[TestAction.create_mini_vm, 'vm2', 'memory=random', 'cluster=cluster2'],
		[TestAction.migrate_vm, 'vm1'],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.create_mini_vm, 'vm3', 'cluster=cluster1'],
		[TestAction.create_volume, 'volume1', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.attach_volume, 'vm3', 'volume1'],
		[TestAction.create_volume, 'volume2', 'cluster=cluster1', 'flag=thin,scsi'],
		[TestAction.add_image, 'image1', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.delete_vm_backup, 'vm1-backup1'],
		[TestAction.delete_image, 'image1'],
		[TestAction.expunge_image, 'image1'],
		[TestAction.create_vm_backup, 'vm3', 'vm3-backup2'],
		[TestAction.destroy_vm, 'vm3'],
		[TestAction.recover_vm, 'vm3'],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.resize_data_volume, 'volume1', 5*1024*1024],
		[TestAction.create_volume, 'volume3', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.attach_volume, 'vm2', 'volume3'],
		[TestAction.delete_volume, 'volume3'],
		[TestAction.attach_volume, 'vm1', 'volume1'],
		[TestAction.create_volume_backup, 'volume1', 'volume1-backup4'],
		[TestAction.change_vm_ha, 'vm1'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.use_volume_backup, 'volume1-backup4'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.change_vm_ha, 'vm1'],
		[TestAction.detach_volume, 'volume1'],
		[TestAction.create_mini_vm, 'vm4', 'network=random', 'cluster=cluster1'],
		[TestAction.delete_volume, 'volume1'],
		[TestAction.expunge_volume, 'volume1'],
		[TestAction.start_vm, 'vm3'],
		[TestAction.reboot_vm, 'vm3'],
		[TestAction.attach_volume, 'vm3', 'volume2'],
		[TestAction.create_volume_backup, 'volume2', 'volume2-backup5'],
		[TestAction.detach_volume, 'volume2'],
		[TestAction.create_image_from_volume, 'vm1', 'vm1-image2'],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.delete_volume_backup, 'volume2-backup5'],
])




'''
The final status:
Running:['vm1', 'vm4', 'vm3']
Stopped:['vm2']
Enadbled:['vm3-backup2', 'volume1-backup2', 'volume1-backup4', 'vm1-image2']
attached:[]
Detached:['volume2']
Deleted:['volume3', 'vm1-backup1', 'volume2-backup5']
Expunged:['volume1', 'image1']
Ha:['vm1']
Group:
	vm_backup1:['vm3-backup2', 'volume1-backup2']---vm3@volume1
'''