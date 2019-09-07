import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", checking_point=1, faild_point=100000, path_list=[
		[TestAction.create_mini_vm, 'vm1', 'cluster=cluster2'],
		[TestAction.create_volume, 'volume1', 'flag=scsi'],
		[TestAction.attach_volume, 'vm1', 'volume1'],
		[TestAction.create_volume_backup, 'volume1', 'volume1-backup1'],
		[TestAction.detach_volume, 'volume1'],
		[TestAction.create_mini_vm, 'vm2', 'cluster=cluster2', 'flag=thick'],
		[TestAction.create_mini_vm, 'vm3', 'cluster=cluster1'],
		[TestAction.migrate_vm, 'vm3'],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.create_volume, 'volume2', 'size=random', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.create_volume, 'volume3', 'cluster=cluster2', 'flag=thin,scsi'],
		[TestAction.add_image, 'image1', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.start_vm, 'vm3'],
		[TestAction.create_vm_backup, 'vm3', 'vm3-backup2'],
		[TestAction.stop_vm, 'vm3'],
		[TestAction.use_vm_backup, 'vm3-backup2'],
		[TestAction.delete_image, 'image1'],
		[TestAction.recover_image, 'image1'],
		[TestAction.delete_image, 'image1'],
		[TestAction.expunge_image, 'image1'],
		[TestAction.start_vm, 'vm3'],
		[TestAction.create_vm_backup, 'vm3', 'vm3-backup3'],
		[TestAction.stop_vm, 'vm3'],
		[TestAction.start_vm, 'vm3'],
		[TestAction.reboot_vm, 'vm3'],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.create_image_from_volume, 'vm2', 'vm2-image2'],
		[TestAction.attach_volume, 'vm1', 'volume3'],
		[TestAction.detach_volume, 'volume3'],
		[TestAction.create_volume, 'volume4', 'cluster=cluster1', 'flag=thin,scsi'],
		[TestAction.delete_vm_backup, 'vm3-backup2'],
		[TestAction.create_mini_vm, 'vm4', 'cluster=cluster2', 'flag=thin'],
		[TestAction.delete_volume, 'volume4'],
		[TestAction.expunge_volume, 'volume4'],
		[TestAction.add_image, 'image3', 'root', os.environ.get('isoForVmUrl')],
		[TestAction.create_vm_by_image, 'image3', 'iso', 'vm5', 'cluster=cluster2'],
		[TestAction.create_vm_backup, 'vm5', 'vm5-backup4'],
		[TestAction.resize_volume, 'vm2', 5*1024*1024],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.delete_vm_backup, 'vm5-backup4'],
])




'''
The final status:
Running:[]
Stopped:['vm3', 'vm1', 'vm2', 'vm4', 'vm5']
Enadbled:['volume1-backup1', 'vm3-backup3', 'vm2-image2', 'image3']
attached:[]
Detached:['volume1', 'volume2', 'volume3']
Deleted:['vm3-backup2', 'vm5-backup4']
Expunged:['volume4', 'image1']
Ha:[]
Group:
'''