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
		[TestAction.expunge_vm, 'vm1'],
		[TestAction.migrate_vm, 'vm2'],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.create_volume, 'volume2', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.attach_volume, 'vm2', 'volume2'],
		[TestAction.create_volume, 'volume3', 'cluster=cluster2', 'flag=thick,scsi'],
		[TestAction.add_image, 'image1', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.attach_volume, 'vm2', 'volume3'],
		[TestAction.create_volume_backup, 'volume3', 'volume3-backup2'],
		[TestAction.delete_volume_backup, 'volume3-backup2'],
		[TestAction.delete_image, 'image1'],
		[TestAction.recover_image, 'image1'],
		[TestAction.delete_image, 'image1'],
		[TestAction.expunge_image, 'image1'],
		[TestAction.create_vm_backup, 'vm2', 'vm2-backup3'],
		[TestAction.create_mini_vm, 'vm3', 'cluster=cluster1'],
		[TestAction.reboot_vm, 'vm3'],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.resize_volume, 'vm2', 5*1024*1024],
		[TestAction.create_volume, 'volume4', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.attach_volume, 'vm3', 'volume4'],
		[TestAction.detach_volume, 'volume4'],
		[TestAction.delete_volume, 'volume4'],
		[TestAction.delete_vm_backup, 'vm2-backup3'],
		[TestAction.create_mini_vm, 'vm4', 'cluster=cluster1', 'flag=thick'],
		[TestAction.expunge_volume, 'volume4'],
		[TestAction.add_image, 'image2', 'root', os.environ.get('isoForVmUrl')],
		[TestAction.create_vm_by_image, 'image2', 'iso', 'vm5', 'cluster=cluster1'],
		[TestAction.create_volume, 'volume5', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.attach_volume, 'vm3', 'volume5'],
		[TestAction.start_vm, 'vm3'],
		[TestAction.create_volume_backup, 'volume5', 'volume5-backup7'],
		[TestAction.stop_vm, 'vm3'],
		[TestAction.start_vm, 'vm3'],
		[TestAction.migrate_vm, 'vm3'],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.create_volume, 'volume6', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.attach_volume, 'vm5', 'volume6'],
		[TestAction.create_volume_backup, 'volume6', 'volume6-backup8'],
		[TestAction.stop_vm, 'vm5'],
		[TestAction.use_volume_backup, 'volume6-backup8'],
		[TestAction.start_vm, 'vm5'],
])




'''
The final status:
Running:['vm4', 'vm3', 'vm5']
Stopped:['vm2']
Enadbled:['volume1-backup1', 'volume5-backup7', 'volume6-backup8', 'image2']
attached:['volume1', 'volume2', 'volume3', 'volume5', 'volume6']
Detached:[]
Deleted:['volume3-backup2', 'vm2-backup3', 'volume1-backup3', 'volume2-backup3', 'volume3-backup3']
Expunged:['vm1', 'volume4', 'image1']
Ha:[]
Group:
'''