import zstackwoodpecker.test_state as ts_header
TestAction = ts_header.TestAction
def path():
    return dict(initial_formation="template5", path_list=[
        [TestAction.create_mini_vm, "vm1", "data_volume=false", "cpu=2", "memory=2", "provisiong=thin"],
        [TestAction.reboot_vm, "vm1"],
        [TestAction.create_volume_backup, "vm1-root", "root-backup1"],
        [TestAction.create_mini_vm, "vm2", "data_volume=false", "cpu=2", "memory=2", "provisiong=thick"],
        [TestAction.create_volume, "volume1", "=scsi,thick"],
        [TestAction.create_mini_vm, "vm3", "data_volume=false", "cpu=2", "memory=2", "network=random", "provisiong=thick"],
        [TestAction.delete_volume, "volume1"],
        [TestAction.add_image, "image1", "root", "http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2"],
        [TestAction.stop_vm, "vm1"],
        [TestAction.use_volume_backup, "data-backup1"],
        [TestAction.start_vm, "vm1"],
        [TestAction.delete_image, "image1"],
        [TestAction.recover_image, "image1"],
        [TestAction.expunge_image, "image1"],
        [TestAction.create_volume_backup, "root-backup2"],
        [TestAction.change_vm_ha, "vm3"],
        [TestAction.create_volume, "volume2", "=scsi,thick"],
        [TestAction.create_volume, "volume3", "=scsi,thick"],
        [TestAction.create_mini_vm, "vm4", "data_volume=false", "cpu=2", "memory=2", "provisiong=thin"],
        [TestAction.add_image, "image2", "root", "http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2"],
        [TestAction.delete_volume, "volume3"],
        [TestAction.create_mini_vm, "vm5", "data_volume=false", "cpu=2", "memory=2", "provisiong=thick"],
        [TestAction.attach_volume, "vm5", "volume2"],
        [TestAction.create_volume_backup, "volume2", "data-backup2"],
        [TestAction.delete_image, "image2"],
        [TestAction.stop_vm, "vm5"],
        [TestAction.use_volume_backup, "data-backup2"],
        [TestAction.add_image, "image3", "root", "http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2"],
        [TestAction.create_volume, "volume4", "=scsi,thick"]
       ])