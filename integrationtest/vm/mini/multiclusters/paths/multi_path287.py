import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", checking_point=1, faild_point=100000, path_list=[
		[TestAction.create_mini_vm, 'vm1', 'cluster=cluster2'],
		[TestAction.reboot_vm, 'vm1'],
		[TestAction.create_mini_vm, 'vm2', 'cluster=cluster1'],
		[TestAction.create_vm_backup, 'vm2', 'vm2-backup1'],
		[TestAction.create_mini_vm, 'vm3', 'network=random', 'cluster=cluster2'],
		[TestAction.resize_volume, 'vm2', 5*1024*1024],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.create_volume, 'volume1', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.attach_volume, 'vm3', 'volume1'],
		[TestAction.detach_volume, 'volume1'],
		[TestAction.delete_volume, 'volume1'],
		[TestAction.add_image, 'image1', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.recover_volume, 'volume1'],
		[TestAction.attach_volume, 'vm1', 'volume1'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.create_volume_backup, 'volume1', 'volume1-backup2'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.use_volume_backup, 'volume1-backup2'],
		[TestAction.detach_volume, 'volume1'],
		[TestAction.delete_image, 'image1'],
		[TestAction.expunge_image, 'image1'],
		[TestAction.attach_volume, 'vm2', 'volume1'],
		[TestAction.create_volume_backup, 'volume1', 'volume1-backup3'],
		[TestAction.detach_volume, 'volume1'],
		[TestAction.change_vm_ha, 'vm3'],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.resize_volume, 'vm3', 5*1024*1024],
		[TestAction.attach_volume, 'vm3', 'volume1'],
		[TestAction.create_volume, 'volume2', 'cluster=cluster1', 'flag=thick,scsi'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.create_vm_backup, 'vm1', 'vm1-backup4'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.use_vm_backup, 'vm1-backup4'],
		[TestAction.create_mini_vm, 'vm4', 'cluster=cluster1', 'flag=thick'],
		[TestAction.delete_volume, 'volume1'],
		[TestAction.expunge_volume, 'volume1'],
		[TestAction.add_image, 'image2', 'root', os.environ.get('isoForVmUrl')],
		[TestAction.create_vm_by_image, 'image2', 'iso', 'vm5', 'cluster=cluster1'],
		[TestAction.attach_volume, 'vm5', 'volume2'],
		[TestAction.create_volume_backup, 'volume2', 'volume2-backup5'],
		[TestAction.detach_volume, 'volume2'],
		[TestAction.migrate_vm, 'vm2'],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.delete_volume_backup, 'volume2-backup5'],
])




'''
The final status:
Running:['vm2', 'vm3', 'vm4', 'vm5']
Stopped:['vm1']
Enadbled:['vm2-backup1', 'volume1-backup2', 'volume1-backup3', 'vm1-backup4', 'image2']
attached:[]
Detached:['volume2']
Deleted:['volume2-backup5']
Expunged:['volume1', 'image1']
Ha:['vm3']
Group:
	vm_backup2:['vm1-backup4']---vm1@
	vm_backup1:['vm2-backup1']---vm2@
'''