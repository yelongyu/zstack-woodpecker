import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", checking_point=1, faild_point=100000, path_list=[
		[TestAction.create_mini_vm, 'vm1', 'cluster=cluster2'],
		[TestAction.change_vm_ha, 'vm1'],
		[TestAction.create_mini_vm, 'vm2', 'cluster=cluster1'],
		[TestAction.create_volume, 'volume1', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.attach_volume, 'vm2', 'volume1'],
		[TestAction.create_volume_backup, 'volume1', 'volume1-backup1'],
		[TestAction.create_mini_vm, 'vm3', 'cpu=random', 'cluster=cluster1'],
		[TestAction.create_image_from_volume, 'vm3', 'vm3-image1'],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.create_volume, 'volume2', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.attach_volume, 'vm2', 'volume2'],
		[TestAction.create_volume, 'volume3', 'cluster=cluster1', 'flag=thin,scsi'],
		[TestAction.add_image, 'image2', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.start_vm, 'vm2'],
		[TestAction.create_vm_backup, 'vm2', 'vm2-backup2'],
		[TestAction.stop_vm, 'vm2'],
		[TestAction.use_vm_backup, 'vm2-backup2'],
		[TestAction.delete_image, 'image2'],
		[TestAction.recover_image, 'image2'],
		[TestAction.delete_image, 'vm3-image1'],
		[TestAction.expunge_image, 'vm3-image1'],
		[TestAction.create_volume, 'volume4', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.attach_volume, 'vm1', 'volume4'],
		[TestAction.create_volume_backup, 'volume4', 'volume4-backup5'],
		[TestAction.add_image, 'image3', 'root', os.environ.get('isoForVmUrl')],
		[TestAction.create_vm_by_image, 'image3', 'iso', 'vm4', 'cluster=cluster2'],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.resize_data_volume, 'volume4', 5*1024*1024],
		[TestAction.create_volume, 'volume5', 'size=random', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.delete_volume, 'volume3'],
		[TestAction.delete_volume_backup, 'volume2-backup2'],
		[TestAction.start_vm, 'vm2'],
		[TestAction.expunge_volume, 'volume3'],
		[TestAction.create_mini_vm, 'vm5', 'data_volume=true', 'cluster=cluster2'],
		[TestAction.create_volume, 'volume7', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.attach_volume, 'vm3', 'volume7'],
		[TestAction.start_vm, 'vm3'],
		[TestAction.create_volume_backup, 'volume7', 'volume7-backup6'],
		[TestAction.stop_vm, 'vm3'],
		[TestAction.resize_volume, 'vm4', 5*1024*1024],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.attach_volume, 'vm5', 'volume5'],
		[TestAction.start_vm, 'vm5'],
		[TestAction.create_volume_backup, 'volume5', 'volume5-backup7'],
		[TestAction.stop_vm, 'vm5'],
		[TestAction.delete_volume_backup, 'volume5-backup7'],
])




'''
The final status:
Running:['vm1', 'vm2']
Stopped:['vm3', 'vm4', 'vm5']
Enadbled:['volume1-backup1', 'vm2-backup2', 'volume1-backup2', 'volume4-backup5', 'volume7-backup6', 'image2', 'image3']
attached:['volume1', 'volume2', 'volume4', 'auto-volume5', 'volume7', 'volume5']
Detached:[]
Deleted:['volume2-backup2', 'volume5-backup7']
Expunged:['volume3', 'vm3-image1']
Ha:['vm1']
Group:
	vm_backup1:['vm2-backup2', 'volume1-backup2', 'volume2-backup2']---vm2@volume1_volume2
'''