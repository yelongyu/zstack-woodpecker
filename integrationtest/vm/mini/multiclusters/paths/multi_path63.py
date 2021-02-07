import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", checking_point=1, faild_point=100000, path_list=[
		[TestAction.create_mini_vm, 'vm1', 'cluster=cluster2'],
		[TestAction.create_mini_vm, 'vm2', 'cluster=cluster1'],
		[TestAction.create_volume, 'volume1', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.attach_volume, 'vm2', 'volume1'],
		[TestAction.create_volume_backup, 'volume1', 'volume1-backup1'],
		[TestAction.create_mini_vm, 'vm3', 'memory=random', 'cluster=cluster1'],
		[TestAction.create_image_from_volume, 'vm1', 'vm1-image1'],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.create_volume, 'volume2', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.attach_volume, 'vm3', 'volume2'],
		[TestAction.create_volume, 'volume3', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.delete_volume, 'volume3'],
		[TestAction.add_image, 'image2', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
		[TestAction.start_vm, 'vm3'],
		[TestAction.create_vm_backup, 'vm3', 'vm3-backup2'],
		[TestAction.delete_vm_backup, 'vm3-backup2'],
		[TestAction.stop_vm, 'vm3'],
		[TestAction.delete_image, 'image2'],
		[TestAction.recover_image, 'image2'],
		[TestAction.delete_image, 'image2'],
		[TestAction.expunge_image, 'image2'],
		[TestAction.create_volume, 'volume4', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.attach_volume, 'vm1', 'volume4'],
		[TestAction.create_volume_backup, 'volume4', 'volume4-backup4'],
		[TestAction.create_mini_vm, 'vm4', 'data_volume=true', 'cluster=cluster2'],
		[TestAction.poweroff_only, 'cluster=cluster2'],
		[TestAction.resize_volume, 'vm4', 5*1024*1024],
		[TestAction.create_volume, 'volume6', 'size=random', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.create_volume, 'volume7', 'cluster=cluster1', 'flag=thin,scsi'],
		[TestAction.attach_volume, 'vm3', 'volume7'],
		[TestAction.start_vm, 'vm3'],
		[TestAction.create_volume_backup, 'volume7', 'volume7-backup5'],
		[TestAction.stop_vm, 'vm3'],
		[TestAction.delete_volume_backup, 'volume7-backup5'],
		[TestAction.create_mini_vm, 'vm5', 'cluster=cluster2', 'flag=thick'],
		[TestAction.delete_volume, 'volume6'],
		[TestAction.expunge_volume, 'volume6'],
		[TestAction.add_image, 'image3', 'root', os.environ.get('isoForVmUrl')],
		[TestAction.create_vm_by_image, 'image3', 'iso', 'vm6', 'cluster=cluster1'],
		[TestAction.create_volume, 'volume8', 'cluster=cluster2', 'flag=scsi'],
		[TestAction.attach_volume, 'vm5', 'volume8'],
		[TestAction.create_volume_backup, 'volume8', 'volume8-backup6'],
		[TestAction.create_image_from_volume, 'vm6', 'vm6-image4'],
		[TestAction.poweroff_only, 'cluster=cluster1'],
		[TestAction.create_volume, 'volume9', 'cluster=cluster1', 'flag=scsi'],
		[TestAction.attach_volume, 'vm6', 'volume9'],
		[TestAction.start_vm, 'vm6'],
		[TestAction.create_volume_backup, 'volume9', 'volume9-backup7'],
		[TestAction.stop_vm, 'vm6'],
		[TestAction.delete_volume_backup, 'volume9-backup7'],
])




'''
The final status:
Running:['vm5']
Stopped:['vm2', 'vm1', 'vm4', 'vm3', 'vm6']
Enadbled:['volume1-backup1', 'volume4-backup4', 'volume8-backup6', 'vm1-image1', 'image3', 'vm6-image4']
attached:['volume1', 'volume2', 'volume4', 'auto-volume4', 'volume7', 'volume8', 'volume9']
Detached:[]
Deleted:['volume3', 'vm3-backup2', 'volume2-backup2', 'volume7-backup5', 'volume9-backup7']
Expunged:['volume6', 'image2']
Ha:[]
Group:
'''