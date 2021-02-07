import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", path_list=[
[TestAction.create_mini_vm, 'vm1', ],
[TestAction.change_vm_ha, 'vm1'],
[TestAction.create_vm_backup, 'vm1', 'vm1-backup1'],
[TestAction.create_mini_vm, 'vm2', ],
[TestAction.stop_vm, 'vm2'],
[TestAction.migrate_vm, 'vm1'],
[TestAction.create_volume, 'volume1', 'flag=scsi'],
[TestAction.attach_volume, 'vm1', 'volume1'],
[TestAction.create_mini_vm, 'vm3', 'network=random'],
[TestAction.create_volume, 'volume2', 'flag=thin,scsi'],
[TestAction.add_image, 'image1', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
[TestAction.start_vm, 'vm2'],
[TestAction.create_vm_backup, 'vm2', 'vm2-backup2'],
[TestAction.stop_vm, 'vm2'],
[TestAction.use_vm_backup, 'vm2-backup2'],
[TestAction.delete_image, 'image1'],
[TestAction.expunge_image, 'image1'],
[TestAction.attach_volume, 'vm1', 'volume2'],
[TestAction.create_volume_backup, 'volume2', 'volume2-backup3'],
[TestAction.detach_volume, 'volume2'],
[TestAction.destroy_vm, 'vm1'],
[TestAction.recover_vm, 'vm1'],
[TestAction.create_image_from_volume, 'vm1', 'vm1-image2'],
[TestAction.destroy_vm, 'vm1'],
[TestAction.attach_volume, 'vm2', 'volume1'],
[TestAction.detach_volume, 'volume1'],
[TestAction.create_volume, 'volume3', 'flag=thin,scsi'],
[TestAction.create_mini_vm, 'vm4', 'flag=thin'],
[TestAction.add_image, 'image3', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
[TestAction.delete_volume, 'volume2'],
[TestAction.expunge_volume, 'volume2'],
[TestAction.reboot_vm, 'vm4'],
[TestAction.create_vm_backup, 'vm4', 'vm4-backup4'],
[TestAction.migrate_vm, 'vm3'],
[TestAction.delete_image, 'vm1-image2'],
[TestAction.recover_image, 'vm1-image2'],
[TestAction.attach_volume, 'vm2', 'volume3'],
[TestAction.start_vm, 'vm2'],
[TestAction.create_volume_backup, 'volume3', 'volume3-backup5'],
[TestAction.delete_volume_backup, 'volume3-backup5'],
[TestAction.stop_vm, 'vm2'],
[TestAction.detach_volume, 'volume3'],
[TestAction.add_image, 'image4', 'root', 'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'],
[TestAction.create_volume, 'volume4', 'flag=scsi'],
[TestAction.attach_volume, 'vm4', 'volume4'],
])



'''
The final status:
Running:['vm3', 'vm4']
Stopped:['vm2']
Enadbled:['vm1-backup1', 'vm2-backup2', 'volume2-backup3', 'vm4-backup4', 'image3', 'vm1-image2', 'image4']
attached:['volume4']
Detached:['volume1', 'volume3']
Deleted:['vm1', 'volume3-backup5']
Expunged:['volume2', 'image1']
Ha:[]
Group:
vm_backup2:['vm2-backup2']---vm2_
vm_backup3:['vm4-backup4']---vm4_
vm_backup1:['vm1-backup1']---vm1_
'''
