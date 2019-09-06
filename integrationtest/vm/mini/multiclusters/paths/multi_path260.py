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
		[TestAction.create_mini_vm, 'vm2', 'cpu=random', 'cluster=cluster1'],
		[TestAction.create_image_from_volume, 'vm1', 'vm1-image2'],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.create_volume, 'volume2', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.attach_volume, 'vm2', 'volume2'],
		[TestAction.detach_volume, 'volume2'],
		[TestAction.create_volume, 'volume3', 'cluster=cluster1', 'flag=thin,scsi'],
		[TestAction.add_image, 'image3', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.start_vm, 'vm2'],
		[TestAction.create_vm_backup, 'vm2', 'vm2-backup2'],
		[TestAction.delete_vm_backup, 'vm2-backup2'],
		[TestAction.stop_vm, 'vm2'],
		[TestAction.delete_image, 'image1'],
		[TestAction.delete_image, 'vm1-image2'],
		[TestAction.expunge_image, 'vm1-image2'],
		[TestAction.attach_volume, 'vm1', 'volume3'],
		[TestAction.create_volume_backup, 'volume3', 'volume3-backup3'],
		[TestAction.detach_volume, 'volume3'],
		[TestAction.reboot_vm, 'vm1'],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.resize_data_volume, 'volume2', 5*1024*1024],
		[TestAction.create_volume, 'volume4', 'size=random', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.create_volume, 'volume5', 'cluster=cluster1', 'flag=thin,scsi'],
		[TestAction.delete_volume_backup, 'volume1-backup1'],
		[TestAction.create_mini_vm, 'vm3', 'network=random', 'cluster=cluster1'],
		[TestAction.delete_volume, 'volume3'],
		[TestAction.expunge_volume, 'volume3'],
		[TestAction.reboot_vm, 'vm3'],
		[TestAction.attach_volume, 'vm1', 'volume4'],
		[TestAction.create_volume_backup, 'volume4', 'volume4-backup4'],
		[TestAction.detach_volume, 'volume4'],
		[TestAction.resize_volume, 'vm3', 5*1024*1024],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.start_vm, 'vm2'],
		[TestAction.create_vm_backup, 'vm2', 'vm2-backup5'],
		[TestAction.delete_vm_backup, 'vm2-backup5'],
		[TestAction.stop_vm, 'vm2'],
])




'''
The final status:
Running:['vm1']
Stopped:['vm3', 'vm2']
Enadbled:['volume3-backup3', 'volume4-backup4', 'image3']
attached:[]
Detached:['volume1', 'volume2', 'volume5', 'volume4']
Deleted:['vm2-backup2', 'volume1-backup1', 'vm2-backup5', 'image1']
Expunged:['volume3', 'vm1-image2']
Ha:[]
Group:
'''