import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", path_list=[
[TestAction.create_mini_vm, 'vm1', 'data_volume=true'],
[TestAction.create_volume, 'volume1', 'flag=scsi'],
[TestAction.attach_volume, 'vm1', 'volume1'],
[TestAction.create_volume_backup, 'volume1', 'volume1-backup1'],
[TestAction.detach_volume, 'volume1'],
[TestAction.create_mini_vm, 'vm2', 'flag=thick'],
[TestAction.resize_data_volume, 'volume1', 5*1024*1024],
[TestAction.attach_volume, 'vm2', 'volume1'],
[TestAction.detach_volume, 'volume1'],
[TestAction.create_mini_vm, 'vm3', 'network=random'],
[TestAction.delete_volume, 'volume1'],
[TestAction.add_image, 'image1', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
[TestAction.delete_volume_backup, 'volume1-backup1'],
[TestAction.delete_image, 'image1'],
[TestAction.recover_image, 'image1'],
[TestAction.delete_image, 'image1'],
[TestAction.expunge_image, 'image1'],
[TestAction.create_vm_backup, 'vm1', 'vm1-backup2'],
[TestAction.change_vm_ha, 'vm1'],
[TestAction.resize_volume, 'vm3', 5*1024*1024],
[TestAction.create_volume, 'volume2', 'flag=scsi'],
[TestAction.attach_volume, 'vm1', 'volume2'],
[TestAction.create_volume, 'volume3', 'flag=thin,scsi'],
[TestAction.create_mini_vm, 'vm4', 'cpu=random'],
[TestAction.add_image, 'image2', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
[TestAction.delete_volume, 'volume3'],
[TestAction.expunge_volume, 'volume3'],
[TestAction.create_mini_vm, 'vm5', 'data_volume=true'],
[TestAction.create_volume_backup, 'volume2', 'volume2-backup3'],
[TestAction.resize_data_volume, 'volume2', 5*1024*1024],
[TestAction.delete_image, 'image2'],
[TestAction.delete_vm_backup, 'vm1-backup2'],
[TestAction.add_image, 'image3', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
[TestAction.detach_volume, 'volume2'],
])



'''
The final status:
Running:['vm1', 'vm2', 'vm3', 'vm4', 'vm5']
Stopped:[]
Enadbled:['volume2-backup3', 'image3']
attached:[]
Detached:['volume2']
Deleted:['volume1', 'volume1-backup1', 'vm1-backup2', 'image2']
Expunged:['volume3', 'image1']
Ha:['vm1']
Group:
'''
