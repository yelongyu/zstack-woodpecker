import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", checking_point=1, faild_point=100000, path_list=[
		[TestAction.add_image, 'image1', 'root', os.environ.get('isoForVmUrl')],
		[TestAction.create_vm_by_image, 'image1', 'iso', 'vm1', 'cluster=cluster2'],
		[TestAction.create_vm_backup, 'vm1', 'vm1-backup1'],
		[TestAction.destroy_vm, 'vm1'],
		[TestAction.expunge_vm, 'vm1'],
		[TestAction.create_mini_vm, 'vm2', 'cluster=cluster1'],
		[TestAction.migrate_vm, 'vm2'],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.create_volume, 'volume1', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.create_mini_vm, 'vm3', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.attach_volume, 'vm3', 'volume1'],
		[TestAction.detach_volume, 'volume1'],
		[TestAction.create_volume, 'volume2', 'cluster=cluster1', 'flag=thin,scsi'],
		[TestAction.add_image, 'image2', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.attach_volume, 'vm3', 'volume1'],
		[TestAction.create_volume_backup, 'volume1', 'volume1-backup2'],
		[TestAction.delete_volume_backup, 'volume1-backup2'],
		[TestAction.delete_image, 'image2'],
		[TestAction.recover_image, 'image2'],
		[TestAction.delete_image, 'image1'],
		[TestAction.expunge_image, 'image1'],
		[TestAction.create_volume, 'volume3', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.attach_volume, 'vm3', 'volume3'],
		[TestAction.create_volume_backup, 'volume3', 'volume3-backup3'],
		[TestAction.destroy_vm, 'vm3'],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.resize_data_volume, 'volume2', 5*1024*1024],
		[TestAction.create_mini_vm, 'vm4', 'cluster=cluster2'],
		[TestAction.attach_volume, 'vm4', 'volume3'],
		[TestAction.create_volume, 'volume4', 'cluster=cluster1', 'flag=thick,scsi'],
		[TestAction.delete_volume_backup, 'volume3-backup3'],
		[TestAction.destroy_vm, 'vm4'],
		[TestAction.expunge_vm, 'vm4'],
		[TestAction.delete_volume, 'volume2'],
		[TestAction.expunge_volume, 'volume2'],
		[TestAction.add_image, 'image3', 'root', os.environ.get('isoForVmUrl')],
		[TestAction.create_vm_by_image, 'image3', 'iso', 'vm5', 'cluster=cluster2'],
		[TestAction.start_vm, 'vm2'],
		[TestAction.create_vm_backup, 'vm2', 'vm2-backup4'],
		[TestAction.stop_vm, 'vm2'],
		[TestAction.resize_data_volume, 'volume4', 5*1024*1024],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.attach_volume, 'vm2', 'volume4'],
		[TestAction.start_vm, 'vm2'],
		[TestAction.create_volume_backup, 'volume4', 'volume4-backup5'],
		[TestAction.stop_vm, 'vm2'],
		[TestAction.use_volume_backup, 'volume4-backup5'],
])




'''
The final status:
Running:['vm5']
Stopped:['vm2']
Enadbled:['vm1-backup1', 'vm2-backup4', 'volume4-backup5', 'image2', 'image3']
attached:['volume4']
Detached:['volume1', 'volume3']
Deleted:['vm3', 'volume1-backup2', 'volume3-backup3']
Expunged:['vm1', 'vm4', 'volume2', 'image1']
Ha:[]
Group:
	vm_backup2:['vm2-backup4']---vm2@
	vm_backup1:['vm1-backup1']---vm1@
'''