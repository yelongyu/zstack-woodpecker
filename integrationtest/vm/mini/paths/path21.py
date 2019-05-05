import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():
    return dict(initial_formation="template5", path_list=[
        [TestAction.create_mini_vm, "vm1", 'data_volume=true', 'cpu=2', 'memory=2', 'provisiong=thick'],
        [TestAction.create_volume_backup, "vm1-root", "backup1"],
        [TestAction.stop_vm, "vm1"],
        [TestAction.start_vm, "vm1"],
        [TestAction.create_volume, "volume1", "=scsi,thin"],
        [TestAction.attach_volume, "vm1", "volume1"],
        [TestAction.create_volume, "volume2", "=scsi,thin"],
        [TestAction.add_image, "image1", 'root', "http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2"],
        [TestAction.create_volume_backup, "volume1", "backup2"],
        [TestAction.delete_volume_backup, "backup2"],
        [TestAction.delete_image, "image1"],
        [TestAction.expunge_image, "image1"],
        [TestAction.create_volume_backup, "volume1", "backup3"],
        [TestAction.create_mini_vm, "vm2", 'data_volume=true', 'cpu=2', 'memory=2', 'provisiong=thick'],
        [TestAction.create_volume, "volume2", "=scsi,thin"],
        [TestAction.attach_volume, "vm2", "volume2"],
        [TestAction.create_volume, "volume3", "=scsi,thick"],
        [TestAction.create_mini_vm, "vm3", 'data_volume=false', 'cpu=random', 'memory=2', 'provisiong=thick'],
        [TestAction.add_image, "image2", 'root', "http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2"],
        [TestAction.delete_volume, "volume2"],
        [TestAction.expunge_volume, "volume2"],
        [TestAction.delete_vm, "vm3"],
        [TestAction.recover_vm, "vm3"],
        [TestAction.create_volume_backup, "vm2-root", "backup4"],
        [TestAction.delete_image, "image2"],
        [TestAction.recover_image, "image2"],
        [TestAction.delete_volume_backup, "backup3"],
        [TestAction.add_image, "image3", 'root', "http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2"],
        [TestAction.create_volume, "volume3", "=scsi,thick"]])