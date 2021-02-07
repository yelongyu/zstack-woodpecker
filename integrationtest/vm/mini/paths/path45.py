import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", path_list=[
[TestAction.create_mini_vm, 'vm1', ],
[TestAction.destroy_vm, 'vm1'],
[TestAction.create_mini_vm, 'vm2', ],
[TestAction.create_vm_backup, 'vm2', 'vm2-backup1'],
[TestAction.create_mini_vm, 'vm3', 'memory=random'],
[TestAction.migrate_vm, 'vm3'],
[TestAction.create_volume, 'volume1', 'flag=scsi'],
[TestAction.attach_volume, 'vm3', 'volume1'],
[TestAction.detach_volume, 'volume1'],
[TestAction.create_mini_vm, 'vm4', 'network=random'],
[TestAction.create_volume, 'volume2', 'flag=thick,scsi'],
[TestAction.add_image, 'image1', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
[TestAction.delete_vm_backup, 'vm2-backup1'],
[TestAction.delete_image, 'image1'],
[TestAction.expunge_image, 'image1'],
[TestAction.attach_volume, 'vm2', 'volume2'],
[TestAction.create_volume_backup, 'volume2', 'volume2-backup2'],
[TestAction.detach_volume, 'volume2'],
[TestAction.add_image, 'image2', 'root', os.environ.get('isoForVmUrl')],
[TestAction.create_vm_by_image, 'image2', 'iso', 'vm5'],
[TestAction.create_image_from_volume, 'vm2', 'vm2-image3'],
[TestAction.attach_volume, 'vm2', 'volume1'],
[TestAction.detach_volume, 'volume1'],
[TestAction.delete_volume, 'volume2'],
[TestAction.recover_volume, 'volume2'],
[TestAction.create_mini_vm, 'vm6', 'cpu=random'],
[TestAction.add_image, 'image4', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
[TestAction.delete_volume, 'volume1'],
[TestAction.expunge_volume, 'volume1'],
[TestAction.destroy_vm, 'vm2'],
[TestAction.recover_vm, 'vm2'],
[TestAction.create_vm_backup, 'vm3', 'vm3-backup3'],
[TestAction.migrate_vm, 'vm4'],
[TestAction.delete_image, 'image2'],
[TestAction.attach_volume, 'vm6', 'volume2'],
[TestAction.stop_vm, 'vm6'],
[TestAction.use_volume_backup, 'volume2-backup2'],
[TestAction.start_vm, 'vm6'],
[TestAction.detach_volume, 'volume2'],
[TestAction.add_image, 'image5', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
[TestAction.create_volume, 'volume3', 'flag=scsi'],
[TestAction.attach_volume, 'vm4', 'volume3'],
])



'''
The final status:
Running:['vm3', 'vm4', 'vm5', 'vm6']
Stopped:['vm2']
Enadbled:['volume2-backup2', 'vm3-backup3', 'vm2-image3', 'image4', 'image5']
attached:['volume3']
Detached:['volume2']
Deleted:['vm1', 'vm2-backup1', 'image2']
Expunged:['volume1', 'image1']
Ha:[]
Group:
vm_backup1:['vm3-backup3']---vm3_
'''
