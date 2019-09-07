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
		[TestAction.create_mini_vm, 'vm2', 'cluster=cluster2'],
		[TestAction.stop_vm, 'vm2'],
		[TestAction.start_vm, 'vm2'],
		[TestAction.create_image_from_volume, 'vm2', 'vm2-image2'],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.create_volume, 'volume2', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.attach_volume, 'vm2', 'volume2'],
		[TestAction.detach_volume, 'volume2'],
		[TestAction.create_volume, 'volume3', 'cluster=cluster2', 'flag=thin,scsi'],
		[TestAction.add_image, 'image3', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.delete_volume_backup, 'volume1-backup1'],
		[TestAction.delete_image, 'image1'],
		[TestAction.recover_image, 'image1'],
		[TestAction.delete_image, 'image1'],
		[TestAction.expunge_image, 'image1'],
		[TestAction.attach_volume, 'vm2', 'volume2'],
		[TestAction.create_volume_backup, 'volume2', 'volume2-backup2'],
		[TestAction.detach_volume, 'volume2'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.reboot_vm, 'vm1'],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.start_vm, 'vm2'],
		[TestAction.migrate_vm, 'vm2'],
		[TestAction.attach_volume, 'vm2', 'volume3'],
		[TestAction.create_volume, 'volume4', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.delete_volume, 'volume4'],
		[TestAction.recover_volume, 'volume4'],
		[TestAction.delete_volume_backup, 'volume2-backup2'],
		[TestAction.start_vm, 'vm2'],
		[TestAction.stop_vm, 'vm2'],
		[TestAction.delete_volume, 'volume2'],
		[TestAction.expunge_volume, 'volume2'],
		[TestAction.add_image, 'image4', 'root', os.environ.get('isoForVmUrl')],
		[TestAction.create_vm_by_image, 'image4', 'iso', 'vm3', 'cluster=cluster2'],
		[TestAction.start_vm, 'vm2'],
		[TestAction.create_volume_backup, 'volume3', 'volume3-backup3'],
		[TestAction.stop_vm, 'vm2'],
		[TestAction.resize_volume, 'vm1', 5*1024*1024],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.use_volume_backup, 'volume3-backup3'],
])




'''
The final status:
Running:['vm1']
Stopped:['vm2', 'vm3']
Enadbled:['volume3-backup3', 'vm2-image2', 'image3', 'image4']
attached:['volume3']
Detached:['volume1', 'volume4']
Deleted:['volume1-backup1', 'volume2-backup2']
Expunged:['volume2', 'image1']
Ha:[]
Group:
'''