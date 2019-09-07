import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", checking_point=1, faild_point=100000, path_list=[
		[TestAction.create_mini_vm, 'vm1', 'cluster=cluster1'],
		[TestAction.change_vm_ha, 'vm1'],
		[TestAction.create_volume, 'volume1', 'flag=scsi'],
		[TestAction.attach_volume, 'vm1', 'volume1'],
		[TestAction.create_volume_backup, 'volume1', 'volume1-backup1'],
		[TestAction.detach_volume, 'volume1'],
		[TestAction.destroy_vm, 'vm1'],
		[TestAction.expunge_vm, 'vm1'],
		[TestAction.create_mini_vm, 'vm2', 'cluster=cluster1'],
		[TestAction.create_image_from_volume, 'vm2', 'vm2-image1'],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.create_volume, 'volume2', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.attach_volume, 'vm2', 'volume2'],
		[TestAction.create_volume, 'volume3', 'cluster=cluster2', 'flag=thick,scsi'],
		[TestAction.add_image, 'image2', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.create_vm_backup, 'vm2', 'vm2-backup2'],
		[TestAction.delete_vm_backup, 'vm2-backup2'],
		[TestAction.delete_image, 'image2'],
		[TestAction.recover_image, 'image2'],
		[TestAction.delete_image, 'image2'],
		[TestAction.expunge_image, 'image2'],
		[TestAction.create_mini_vm, 'vm3', 'cluster=cluster2'],
		[TestAction.create_vm_backup, 'vm3', 'vm3-backup4'],
		[TestAction.destroy_vm, 'vm3'],
		[TestAction.recover_vm, 'vm3'],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.create_image_from_volume, 'vm2', 'vm2-image3'],
		[TestAction.create_volume, 'volume4', 'size=random', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.delete_volume, 'volume2'],
		[TestAction.attach_volume, 'vm3', 'volume1'],
		[TestAction.use_volume_backup, 'volume1-backup1'],
		[TestAction.detach_volume, 'volume1'],
		[TestAction.create_mini_vm, 'vm4', 'cluster=cluster2', 'flag=thick'],
		[TestAction.expunge_volume, 'volume2'],
		[TestAction.start_vm, 'vm3'],
		[TestAction.reboot_vm, 'vm3'],
		[TestAction.start_vm, 'vm2'],
		[TestAction.create_vm_backup, 'vm2', 'vm2-backup5'],
		[TestAction.stop_vm, 'vm2'],
		[TestAction.resize_volume, 'vm2', 5*1024*1024],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.use_vm_backup, 'vm2-backup5'],
])




'''
The final status:
Running:['vm4', 'vm3']
Stopped:['vm2']
Enadbled:['volume1-backup1', 'vm3-backup4', 'vm2-backup5', 'vm2-image1', 'vm2-image3']
attached:[]
Detached:['volume3', 'volume4', 'volume1']
Deleted:['vm2-backup2', 'volume2-backup2']
Expunged:['vm1', 'volume2', 'image2']
Ha:[]
Group:
	vm_backup2:['vm2-backup5']---vm2@
	vm_backup1:['vm3-backup4']---vm3@
'''