import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", checking_point=1, faild_point=100000, path_list=[
		[TestAction.create_mini_vm, 'vm1', 'cluster=cluster1'],
		[TestAction.create_volume, 'volume1', 'flag=scsi'],
		[TestAction.attach_volume, 'vm1', 'volume1'],
		[TestAction.create_volume_backup, 'volume1', 'volume1-backup1'],
		[TestAction.detach_volume, 'volume1'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.create_image_from_volume, 'vm1', 'vm1-image1'],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.create_volume, 'volume2', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.attach_volume, 'vm1', 'volume2'],
		[TestAction.create_volume, 'volume3', 'cluster=cluster1', 'flag=thick,scsi'],
		[TestAction.add_image, 'image2', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.create_vm_backup, 'vm1', 'vm1-backup2'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.use_vm_backup, 'vm1-backup2'],
		[TestAction.delete_image, 'vm1-image1'],
		[TestAction.recover_image, 'vm1-image1'],
		[TestAction.delete_image, 'vm1-image1'],
		[TestAction.expunge_image, 'vm1-image1'],
		[TestAction.attach_volume, 'vm1', 'volume1'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.create_volume_backup, 'volume1', 'volume1-backup4'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.detach_volume, 'volume1'],
		[TestAction.change_vm_ha, 'vm1'],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.create_mini_vm, 'vm2', 'cluster=cluster2'],
		[TestAction.migrate_vm, 'vm2'],
		[TestAction.attach_volume, 'vm1', 'volume3'],
		[TestAction.create_volume, 'volume4', 'cluster=cluster1', 'flag=thick,scsi'],
		[TestAction.attach_volume, 'vm2', 'volume1'],
		[TestAction.stop_vm, 'vm2'],
		[TestAction.use_volume_backup, 'volume1-backup1'],
		[TestAction.start_vm, 'vm2'],
		[TestAction.detach_volume, 'volume1'],
		[TestAction.create_mini_vm, 'vm3', 'memory=random', 'cluster=cluster1'],
		[TestAction.delete_volume, 'volume2'],
		[TestAction.expunge_volume, 'volume2'],
		[TestAction.add_image, 'image3', 'root', os.environ.get('isoForVmUrl')],
		[TestAction.create_vm_by_image, 'image3', 'iso', 'vm4', 'cluster=cluster2'],
		[TestAction.create_volume_backup, 'volume3', 'volume3-backup5'],
		[TestAction.create_image_from_volume, 'vm3', 'vm3-image4'],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.attach_volume, 'vm1', 'volume1'],
		[TestAction.change_vm_ha, 'vm1'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.use_volume_backup, 'volume1-backup1'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.change_vm_ha, 'vm1'],
		[TestAction.detach_volume, 'volume1'],
])




'''
The final status:
Running:['vm2', 'vm4', 'vm1']
Stopped:['vm3']
Enadbled:['volume1-backup1', 'vm1-backup2', 'volume2-backup2', 'volume1-backup4', 'volume3-backup5', 'image2', 'image3', 'vm3-image4']
attached:['volume3']
Detached:['volume4', 'volume1']
Deleted:[]
Expunged:['volume2', 'vm1-image1']
Ha:['vm1']
Group:
	vm_backup1:['vm1-backup2', 'volume2-backup2']---vm1@volume2
'''