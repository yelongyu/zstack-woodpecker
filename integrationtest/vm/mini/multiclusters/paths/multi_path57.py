import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", checking_point=1, faild_point=100000, path_list=[
		[TestAction.create_mini_vm, 'vm1', 'data_volume=true', 'cluster=cluster1'],
		[TestAction.create_mini_vm, 'vm2', 'cluster=cluster2'],
		[TestAction.create_vm_backup, 'vm2', 'vm2-backup1'],
		[TestAction.create_mini_vm, 'vm3', 'cluster=cluster1', 'flag=thick'],
		[TestAction.create_volume, 'volume2', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.resize_data_volume, 'volume2', 5*1024*1024],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.create_volume, 'volume3', 'size=random', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.create_volume, 'volume4', 'cluster=cluster2', 'flag=thin,scsi'],
		[TestAction.add_image, 'image1', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.create_volume_backup, 'auto-volume1', 'auto-volume1-backup2'],
		[TestAction.delete_volume_backup, 'auto-volume1-backup2'],
		[TestAction.delete_image, 'image1'],
		[TestAction.recover_image, 'image1'],
		[TestAction.delete_image, 'image1'],
		[TestAction.expunge_image, 'image1'],
		[TestAction.start_vm, 'vm2'],
		[TestAction.create_vm_backup, 'vm2', 'vm2-backup3'],
		[TestAction.stop_vm, 'vm2'],
		[TestAction.add_image, 'image2', 'root', os.environ.get('isoForVmUrl')],
		[TestAction.create_vm_by_image, 'image2', 'iso', 'vm4', 'cluster=cluster1'],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.resize_volume, 'vm2', 5*1024*1024],
		[TestAction.attach_volume, 'vm4', 'volume2'],
		[TestAction.delete_volume, 'volume4'],
		[TestAction.create_volume_backup, 'volume2', 'volume2-backup4'],
		[TestAction.delete_volume_backup, 'volume2-backup4'],
		[TestAction.create_mini_vm, 'vm5', 'cluster=cluster1'],
		[TestAction.start_vm, 'vm5'],
		[TestAction.delete_volume, 'volume2'],
		[TestAction.expunge_volume, 'volume2'],
		[TestAction.destroy_vm, 'vm2'],
		[TestAction.create_volume_backup, 'auto-volume1', 'auto-volume1-backup5'],
		[TestAction.create_mini_vm, 'vm6', 'cluster=cluster2'],
		[TestAction.create_image_from_volume, 'vm6', 'vm6-image3'],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.delete_volume_backup, 'auto-volume1-backup5'],
])




'''
The final status:
Running:['vm1', 'vm3', 'vm4', 'vm5']
Stopped:['vm6']
Enadbled:['vm2-backup1', 'vm2-backup3', 'image2', 'vm6-image3']
attached:['auto-volume1']
Detached:['volume3']
Deleted:['vm2', 'volume4', 'auto-volume1-backup2', 'volume2-backup4', 'auto-volume1-backup5']
Expunged:['volume2', 'image1']
Ha:[]
Group:
	vm_backup2:['vm2-backup3']---vm2@
	vm_backup1:['vm2-backup1']---vm2@
'''