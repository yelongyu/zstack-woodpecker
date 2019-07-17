import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", path_list=[
        [TestAction.create_mini_vm, "vm1", 'data_volume=false', 'cpu=random', 'memory=random', 'network=random', 'provisiong=thick'],
        [TestAction.destroy_vm, "vm1"],
        [TestAction.create_mini_vm, "vm2", 'data_volume=false', 'cpu=random', 'memory=random', 'network=random',
         'provisiong=thick'],
        [TestAction.create_vm_backup, "vm2", "backup1"],
        [TestAction.create_mini_vm, "vm3", 'data_volume=false', 'cpu=random', 'memory=random', 'network=random',
         'provisiong=thick'],
        [TestAction.resize_volume, "vm2", 5 * 1024 * 1024],
        [TestAction.resize_volume, "vm3", 5 * 1024 * 1024],
        [TestAction.create_volume, "volume1", "=scsi,thick"],
        [TestAction.attach_volume, "vm2", "volume1"],
        [TestAction.create_mini_vm, "vm4", 'data_volume=false', 'cpu=random', 'memory=random', 'network=random',
         'provisiong=thick'],
        [TestAction.create_volume, "volume2", "=scsi,thick"],
        [TestAction.add_image, "image1", 'root', "http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2"],
        [TestAction.create_volume_backup, "volume1", 'backup2'],
        [TestAction.stop_vm, "vm2"],
        [TestAction.use_volume_backup, "backup2"],
        [TestAction.start_vm, "vm2"],
        [TestAction.delete_image, "image1"],
        [TestAction.recover_image, "image1"],
        [TestAction.delete_image, "image1"],
        [TestAction.expunge_image, "image1"],
        [TestAction.create_volume_backup, "volume1", "backup3"],
        [TestAction.recover_vm, "vm1"],
        [TestAction.start_vm, "vm1"],
        [TestAction.migrate_vm, "vm1"],
        [TestAction.migrate_vm, "vm2"],
        [TestAction.migrate_vm, "vm3"],
        [TestAction.migrate_vm, "vm4"],
        [TestAction.create_mini_vm, "vm5", 'data_volume=true', 'cpu=random', 'memory=random', 'network=random',
         'provisiong=thick'],
        [TestAction.delete_volume, "volume2"],
        [TestAction.create_mini_vm, "vm6", 'data_volume=false', 'cpu=random', 'memory=random', 'network=random',
         'provisiong=thin'],
        [TestAction.add_image, "image2", 'root', "http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2"],
        [TestAction.expunge_volume, "volume2"],
        [TestAction.change_vm_ha, "vm1"],
        [TestAction.change_vm_ha, "vm2"],
        [TestAction.change_vm_ha, "vm3"],
        [TestAction.change_vm_ha, "vm4"],
        [TestAction.change_vm_ha, "vm5"],
        [TestAction.change_vm_ha, "vm6"],
        [TestAction.create_vm_backup, "vm1", "vm1-backup"],
        [TestAction.create_vm_backup, "vm2", "vm2-backup"],
        [TestAction.create_vm_backup, "vm3", "vm3-backup"],
        [TestAction.create_vm_backup, "vm4", "vm4-backup"],
        [TestAction.create_vm_backup, "vm5", "vm5-backup"],
        [TestAction.create_vm_backup, "vm6", "vm6-backup"],
        [TestAction.resize_volume, "vm1", 5 * 1024 * 1024],
        [TestAction.resize_volume, "vm2", 5 * 1024 * 1024],
        [TestAction.resize_volume, "vm3", 5 * 1024 * 1024],
        [TestAction.resize_volume, "vm4", 5 * 1024 * 1024],
        [TestAction.resize_volume, "vm5", 5 * 1024 * 1024],
        [TestAction.resize_volume, "vm6", 5 * 1024 * 1024],
        [TestAction.delete_image, "image2"],
        [TestAction.delete_volume_backup, "backup3"],
        [TestAction.delete_vm_backup, "vm2-backup"],
        [TestAction.add_image, "image3", 'root', "http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2"],
        [TestAction.create_volume, "volume2", "flag=scsi,thick", "size=random"]])