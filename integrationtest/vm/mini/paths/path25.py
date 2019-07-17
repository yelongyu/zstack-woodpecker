import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():
    return dict(initial_formation="template5", path_list=[
        [TestAction.create_mini_vm, "vm1", 'data_volume=true', 'cpu=2', 'memory=2', 'provisiong=thick'],
        [TestAction.create_vm_backup, "vm1", "backup1"],
        [TestAction.create_mini_vm, "vm2", 'data_volume=false', 'cpu=2', 'memory=2', 'provisiong=thin'],
        [TestAction.migrate_vm, "vm1"],
        [TestAction.migrate_vm, "vm2"],
        [TestAction.create_volume, "volume1", "size=random", "flag=scsi,thin"],
        [TestAction.create_mini_vm, "vm3", 'data_volume=false', 'cpu=2', 'memory=2', 'network=random',
         'provisiong=thin'],
        [TestAction.create_volume, "volume2", "size=random", "flag=scsi,thick"],
        [TestAction.add_image, "image1", 'root', "http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2"],
        [TestAction.stop_vm, "vm1"],
        [TestAction.use_vm_backup, "backup1"],
        [TestAction.start_vm, "vm1"],
        [TestAction.delete_image, "image1"],
        [TestAction.expunge_image, "image1"],
        [TestAction.create_vm_backup, "vm1", "backup3"],
        [TestAction.create_vm_backup, "vm2", "backup2"],
        [TestAction.destroy_vm, "vm2"],
        [TestAction.create_image_from_volume, "vm1", "vm1-image1"],
        [TestAction.detach_volume, "volume1"],
        [TestAction.delete_volume, "volume1"],
        [TestAction.recover_volume, "volume1"],
        [TestAction.expunge_vm, "vm2"],
        [TestAction.add_image, "image2", 'root', "http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2"],
        [TestAction.delete_volume, "volume2"],
        [TestAction.expunge_volume, "volume2"],
        [TestAction.create_vm_by_image, "iso1", "iso", "vm4"],
        [TestAction.create_vm_backup, "vm4", "backup4"],
        [TestAction.create_image_from_volume, "vm4", "vm4-image1"],
        [TestAction.delete_image, "vm4-image1"],
        [TestAction.stop_vm, "vm1"],
        [TestAction.stop_vm, "vm4"],
        [TestAction.use_vm_backup, "backup3"],
        [TestAction.use_vm_backup, "backup4"],
        [TestAction.start_vm, "vm1"],
        [TestAction.start_vm, "vm4"],
        [TestAction.add_image, "image3", 'root', "http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2"],
        [TestAction.attach_volume, "vm4", "volume1"],
        [TestAction.detach_volume, "volume1"]])