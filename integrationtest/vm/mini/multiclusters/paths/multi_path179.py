import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", checking_point=1, faild_point=100000, path_list=[
		[TestAction.add_image, 'image1', 'root', os.environ.get('isoForVmUrl')],
		[TestAction.create_vm_by_image, 'image1', 'iso', 'vm1', 'cluster=cluster1'],
		[TestAction.create_volume, 'volume1', 'flag=scsi'],
		[TestAction.attach_volume, 'vm1', 'volume1'],
		[TestAction.create_volume_backup, 'volume1', 'volume1-backup1'],
		[TestAction.detach_volume, 'volume1'],
		[TestAction.create_mini_vm, 'vm2', 'cluster=cluster2', 'flag=thick'],
		[TestAction.migrate_vm, 'vm2'],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.create_volume, 'volume2', 'size=random', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.create_volume, 'volume3', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.delete_volume, 'volume3'],
		[TestAction.add_image, 'image2', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.create_vm_backup, 'vm1', 'vm1-backup2'],
		[TestAction.delete_vm_backup, 'vm1-backup2'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.delete_image, 'image2'],
		[TestAction.delete_image, 'image1'],
		[TestAction.expunge_image, 'image1'],
		[TestAction.attach_volume, 'vm2', 'volume2'],
		[TestAction.create_volume_backup, 'volume2', 'volume2-backup3'],
		[TestAction.detach_volume, 'volume2'],
		[TestAction.add_image, 'image3', 'root', os.environ.get('isoForVmUrl')],
		[TestAction.create_vm_by_image, 'image3', 'iso', 'vm3', 'cluster=cluster1'],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.create_image_from_volume, 'vm2', 'vm2-image4'],
		[TestAction.create_volume, 'volume4', 'size=random', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.create_volume, 'volume5', 'cluster=cluster2', 'flag=thin,scsi'],
		[TestAction.delete_volume_backup, 'volume1-backup1'],
		[TestAction.create_mini_vm, 'vm4', 'cluster=cluster1', 'flag=thin'],
		[TestAction.delete_volume, 'volume2'],
		[TestAction.expunge_volume, 'volume2'],
		[TestAction.destroy_vm, 'vm2'],
		[TestAction.attach_volume, 'vm4', 'volume1'],
		[TestAction.create_volume_backup, 'volume1', 'volume1-backup4'],
		[TestAction.detach_volume, 'volume1'],
		[TestAction.create_image_from_volume, 'vm4', 'vm4-image5'],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.delete_volume_backup, 'volume1-backup4'],
])




'''
The final status:
Running:[]
Stopped:['vm1', 'vm3', 'vm4']
Enadbled:['volume2-backup3', 'image3', 'vm2-image4', 'vm4-image5']
attached:[]
Detached:['volume4', 'volume5', 'volume1']
Deleted:['vm2', 'volume3', 'vm1-backup2', 'volume1-backup1', 'volume1-backup4', 'image2']
Expunged:['volume2', 'image1']
Ha:[]
Group:
'''