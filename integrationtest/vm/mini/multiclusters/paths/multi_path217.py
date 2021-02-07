import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", checking_point=1, faild_point=100000, path_list=[
		[TestAction.create_mini_vm, 'vm1', 'cluster=cluster2'],
		[TestAction.destroy_vm, 'vm1'],
		[TestAction.create_mini_vm, 'vm2', 'cluster=cluster2'],
		[TestAction.create_volume, 'volume1', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.attach_volume, 'vm2', 'volume1'],
		[TestAction.create_volume_backup, 'volume1', 'volume1-backup1'],
		[TestAction.create_mini_vm, 'vm3', 'network=random', 'cluster=cluster1'],
		[TestAction.create_image_from_volume, 'vm3', 'vm3-image1'],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.create_volume, 'volume2', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.attach_volume, 'vm3', 'volume2'],
		[TestAction.detach_volume, 'volume2'],
		[TestAction.create_volume, 'volume3', 'cluster=cluster1', 'flag=thin,scsi'],
		[TestAction.add_image, 'image2', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.start_vm, 'vm2'],
		[TestAction.create_vm_backup, 'vm2', 'vm2-backup2'],
		[TestAction.stop_vm, 'vm2'],
		[TestAction.use_vm_backup, 'vm2-backup2'],
		[TestAction.delete_image, 'image2'],
		[TestAction.delete_image, 'vm3-image1'],
		[TestAction.expunge_image, 'vm3-image1'],
		[TestAction.create_vm_backup, 'vm3', 'vm3-backup4'],
		[TestAction.create_mini_vm, 'vm4', 'cluster=cluster1'],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.start_vm, 'vm3'],
		[TestAction.migrate_vm, 'vm3'],
		[TestAction.create_volume, 'volume4', 'size=random', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.delete_volume, 'volume1'],
		[TestAction.use_vm_backup, 'vm2-backup2'],
		[TestAction.create_mini_vm, 'vm5', 'network=random', 'cluster=cluster1'],
		[TestAction.delete_volume, 'volume3'],
		[TestAction.expunge_volume, 'volume3'],
		[TestAction.destroy_vm, 'vm2'],
		[TestAction.recover_vm, 'vm2'],
		[TestAction.attach_volume, 'vm2', 'volume4'],
		[TestAction.start_vm, 'vm2'],
		[TestAction.create_volume_backup, 'volume4', 'volume4-backup5'],
		[TestAction.stop_vm, 'vm2'],
		[TestAction.create_image_from_volume, 'vm2', 'vm2-image3'],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.recover_volume, 'volume1'],
		[TestAction.use_volume_backup, 'volume1-backup2'],
])




'''
The final status:
Running:['vm3', 'vm5']
Stopped:['vm4', 'vm2']
Enadbled:['volume1-backup1', 'vm2-backup2', 'volume1-backup2', 'vm3-backup4', 'volume4-backup5', 'vm2-image3']
attached:['volume4']
Detached:['volume2', 'volume1']
Deleted:['vm1', 'image2']
Expunged:['volume3', 'vm3-image1']
Ha:[]
Group:
	vm_backup2:['vm3-backup4']---vm3@
	vm_backup1:['vm2-backup2', 'volume1-backup2']---vm2@volume1
'''