import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", checking_point=1, faild_point=100000, path_list=[
		[TestAction.create_mini_vm, 'vm1', 'cluster=cluster2'],
		[TestAction.create_vm_backup, 'vm1', 'vm1-backup1'],
		[TestAction.create_mini_vm, 'vm2', 'network=random', 'cluster=cluster2'],
		[TestAction.create_mini_vm, 'vm3', 'cluster=cluster1'],
		[TestAction.create_image_from_volume, 'vm3', 'vm3-image1'],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.create_volume, 'volume1', 'size=random', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.delete_volume, 'volume1'],
		[TestAction.recover_volume, 'volume1'],
		[TestAction.add_image, 'image2', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.create_volume, 'volume2', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.attach_volume, 'vm2', 'volume2'],
		[TestAction.start_vm, 'vm2'],
		[TestAction.create_volume_backup, 'volume2', 'volume2-backup2'],
		[TestAction.stop_vm, 'vm2'],
		[TestAction.delete_volume_backup, 'volume2-backup2'],
		[TestAction.delete_image, 'vm3-image1'],
		[TestAction.recover_image, 'vm3-image1'],
		[TestAction.delete_image, 'vm3-image1'],
		[TestAction.expunge_image, 'vm3-image1'],
		[TestAction.create_volume, 'volume3', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.attach_volume, 'vm1', 'volume3'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.create_volume_backup, 'volume3', 'volume3-backup3'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.change_vm_ha, 'vm3'],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.resize_volume, 'vm1', 5*1024*1024],
		[TestAction.create_volume, 'volume4', 'size=random', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.create_volume, 'volume5', 'cluster=cluster2', 'flag=thick,scsi'],
		[TestAction.attach_volume, 'vm3', 'volume4'],
		[TestAction.create_volume_backup, 'volume4', 'volume4-backup4'],
		[TestAction.change_vm_ha, 'vm3'],
		[TestAction.stop_vm, 'vm3'],
		[TestAction.use_volume_backup, 'volume4-backup4'],
		[TestAction.start_vm, 'vm3'],
		[TestAction.change_vm_ha, 'vm3'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.delete_volume, 'volume2'],
		[TestAction.expunge_volume, 'volume2'],
		[TestAction.change_vm_ha, 'vm3'],
		[TestAction.create_vm_backup, 'vm1', 'vm1-backup5'],
		[TestAction.resize_data_volume, 'volume4', 5*1024*1024],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.delete_volume_backup, 'volume3-backup5'],
])




'''
The final status:
Running:['vm3']
Stopped:['vm2', 'vm1']
Enadbled:['vm1-backup1', 'volume3-backup3', 'volume4-backup4', 'vm1-backup5', 'image2']
attached:['volume3', 'volume4']
Detached:['volume1', 'volume5']
Deleted:['volume2-backup2', 'volume3-backup5']
Expunged:['volume2', 'vm3-image1']
Ha:[]
Group:
	vm_backup2:['vm1-backup5', 'volume3-backup5']---vm1@volume3
	vm_backup1:['vm1-backup1']---vm1@
'''