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
		[TestAction.create_mini_vm, 'vm2', 'cpu=random', 'cluster=cluster2'],
		[TestAction.create_mini_vm, 'vm3', 'cluster=cluster1'],
		[TestAction.create_image_from_volume, 'vm3', 'vm3-image2'],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.create_volume, 'volume2', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.attach_volume, 'vm3', 'volume2'],
		[TestAction.create_volume, 'volume3', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.delete_volume, 'volume3'],
		[TestAction.add_image, 'image3', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.start_vm, 'vm3'],
		[TestAction.create_vm_backup, 'vm3', 'vm3-backup2'],
		[TestAction.delete_vm_backup, 'vm3-backup2'],
		[TestAction.stop_vm, 'vm3'],
		[TestAction.delete_image, 'image3'],
		[TestAction.recover_image, 'image3'],
		[TestAction.delete_image, 'vm3-image2'],
		[TestAction.expunge_image, 'vm3-image2'],
		[TestAction.start_vm, 'vm3'],
		[TestAction.create_vm_backup, 'vm3', 'vm3-backup4'],
		[TestAction.stop_vm, 'vm3'],
		[TestAction.change_vm_ha, 'vm1'],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.create_image_from_volume, 'vm3', 'vm3-image4'],
		[TestAction.detach_volume, 'volume2'],
		[TestAction.delete_volume, 'volume2'],
		[TestAction.recover_volume, 'volume2'],
		[TestAction.delete_vm_backup, 'vm3-backup4'],
		[TestAction.create_mini_vm, 'vm4', 'memory=random', 'cluster=cluster2'],
		[TestAction.expunge_volume, 'volume3'],
		[TestAction.destroy_vm, 'vm2'],
		[TestAction.create_vm_backup, 'vm4', 'vm4-backup6'],
		[TestAction.migrate_vm, 'vm4'],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.delete_vm_backup, 'vm4-backup6'],
])




'''
The final status:
Running:['vm1', 'vm4']
Stopped:['vm3']
Enadbled:['volume1-backup1', 'image1', 'image3', 'vm3-image4']
attached:[]
Detached:['volume1', 'volume2']
Deleted:['vm2', 'vm3-backup2', 'volume2-backup2', 'vm3-backup4', 'volume2-backup4', 'vm4-backup6']
Expunged:['volume3', 'vm3-image2']
Ha:['vm1']
Group:
'''