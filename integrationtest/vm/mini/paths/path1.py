import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", path_list=[
        [TestAction.create_mini_vm, "vm1", 'data_volume=false', 'cpu=2', 'memory=2', 'provisiong=thin'],
        [TestAction.create_volume, "volume1", "=scsi,thin"],
        [TestAction.attach_volume, "vm1", "volume1"],
        [TestAction.create_volume_backup, "volume1", "backup1"],
        [TestAction.create_mini_vm, "vm2", 'data_volume=false', 'cpu=2', 'memory=random', 'provisiong=thin'],
        [TestAction.resize_volume, "vm1", 5*1024*1024],
        [TestAction.resize_volume, "vm2", 5*1024*1024],
        [TestAction.detach_volume, "volume1"],
        [TestAction.create_mini_vm, "vm3", 'data_volume=false', 'cpu=2', 'memory=2', 'network=random', 'provisiong=thin'],
        [TestAction.delete_volume, "volume1"],
        [TestAction.add_image, "image1", 'root', "http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2"],
        [TestAction.delete_volume_backup, "backup1"],
        [TestAction.delete_image, "image1"],
        [TestAction.expunge_image, "image1"],
        [TestAction.create_volume, "volume2", "=scsi,thin"],
        [TestAction.attach_volume, "vm2", "volume2"],
        [TestAction.create_volume_backup, "volume2", "backup2"],
        [TestAction.reboot_vm, "vm1"],
        [TestAction.reboot_vm, "vm2"],
        [TestAction.reboot_vm, "vm3"],
        [TestAction.resize_volume, "vm1", 5*1024*1024],
        [TestAction.resize_volume, "vm2", 5*1024*1024],
        [TestAction.resize_volume, "vm3", 5*1024*1024],
        [TestAction.create_volume, "volume3", "=scsi,thin"],
        [TestAction.delete_volume, "volume3"],
        [TestAction.destroy_vm, "vm3"],
        [TestAction.expunge_vm, "vm3"],
        [TestAction.add_image, "image2", 'root', "http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2"],
        [TestAction.expunge_volume, "volume1"],
        [TestAction.create_mini_vm, "vm4", 'data_volume=false', 'cpu=2', 'memory=2', 'provisiong=thin'],
        [TestAction.create_vm_backup, "vm4", "backup3"],
        [TestAction.migrate_vm, "vm4"],
        [TestAction.delete_image, "image2"],
        [TestAction.recover_image, "image2"],
        [TestAction.delete_volume_backup, "backup2"],
        [TestAction.add_image, "image3", 'root', "http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2"],
        [TestAction.recover_volume, "volume3"],
        [TestAction.change_vm_ha, 'vm1'],
        [TestAction.create_volume, "volume4", "=scsi,thin"],
        [TestAction.attach_volume, "vm2", "volume4"]])