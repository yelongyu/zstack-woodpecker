import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", checking_point=1, faild_point=100000, path_list=[
		[TestAction.add_image, 'image1', 'root', os.environ.get('isoForVmUrl')],
		[TestAction.create_vm_by_image, 'image1', 'iso', 'vm1', 'cluster=cluster2'],
		[TestAction.create_volume, 'volume1', 'flag=scsi'],
		[TestAction.attach_volume, 'vm1', 'volume1'],
		[TestAction.create_volume_backup, 'volume1', 'volume1-backup1'],
		[TestAction.detach_volume, 'volume1'],
		[TestAction.create_mini_vm, 'vm2', 'cluster=cluster1', 'flag=thin'],
		[TestAction.resize_volume, 'vm2', 5*1024*1024],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.create_volume, 'volume2', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.attach_volume, 'vm1', 'volume2'],
		[TestAction.detach_volume, 'volume2'],
		[TestAction.create_volume, 'volume3', 'cluster=cluster2', 'flag=thin,scsi'],
		[TestAction.add_image, 'image2', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.create_vm_backup, 'vm2', 'vm2-backup2'],
		[TestAction.delete_vm_backup, 'vm2-backup2'],
		[TestAction.delete_image, 'image1'],
		[TestAction.delete_image, 'image2'],
		[TestAction.expunge_image, 'image2'],
		[TestAction.attach_volume, 'vm2', 'volume2'],
		[TestAction.create_volume_backup, 'volume2', 'volume2-backup3'],
		[TestAction.detach_volume, 'volume2'],
		[TestAction.destroy_vm, 'vm2'],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.create_image_from_volume, 'vm1', 'vm1-image3'],
		[TestAction.create_volume, 'volume4', 'size=random', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.create_volume, 'volume5', 'cluster=cluster1', 'flag=thin,scsi'],
		[TestAction.create_vm_backup, 'vm1', 'vm1-backup4'],
		[TestAction.delete_vm_backup, 'vm1-backup4'],
		[TestAction.create_mini_vm, 'vm3', 'cluster=cluster1'],
		[TestAction.start_vm, 'vm3'],
		[TestAction.delete_volume, 'volume3'],
		[TestAction.expunge_volume, 'volume3'],
		[TestAction.change_vm_ha, 'vm3'],
		[TestAction.attach_volume, 'vm3', 'volume5'],
		[TestAction.create_volume_backup, 'volume5', 'volume5-backup5'],
		[TestAction.detach_volume, 'volume5'],
		[TestAction.resize_data_volume, 'volume5', 5*1024*1024],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.create_vm_backup, 'vm1', 'vm1-backup6'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.use_vm_backup, 'vm1-backup6'],
		[TestAction.start_vm, 'vm1'],
])




'''
The final status:
Running:['vm3', 'vm1']
Stopped:[]
Enadbled:['volume1-backup1', 'volume2-backup3', 'volume5-backup5', 'vm1-backup6', 'vm1-image3']
attached:[]
Detached:['volume1', 'volume2', 'volume4', 'volume5']
Deleted:['vm2', 'vm2-backup2', 'vm1-backup4', 'image1']
Expunged:['volume3', 'image2']
Ha:['vm3']
Group:
	vm_backup1:['vm1-backup6']---vm1@
'''