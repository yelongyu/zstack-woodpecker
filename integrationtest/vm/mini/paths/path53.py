import zstackwoodpecker.test_state as ts_header
TestAction = ts_header.TestAction
def path():
    return dict(initial_formation="template5", path_list=[
        [TestAction.create_mini_vm, "vm1", "data_volume=true", "cpu=2", "memory=2","provisiong=thick"],
        [TestAction.create_vm_by_image, "iso1", "iso", "vm2"],
        [TestAction.create_volume, "volume1", "=scsi,thick"],
        [TestAction.attach_volume, "vm1", "volume1"],
        [TestAction.create_volume_backup, "volume1", "data-backup1"],
        [TestAction.stop_vm, "vm1"],
        [TestAction.create_volume, "volume2", "=scsi,thick"],
        [TestAction.create_mini_vm, "vm3", "data_volume=true", "cpu=2", "memory=2","provisiong=thick","network=random"],
        [TestAction.create_volume, "volume3", "=scsi,thin"],
        [TestAction.add_image, "image1", 'root', "http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2"],
        [TestAction.create_volume_backup, "vm1-root", "root-backup1"],
        [TestAction.delete_image, "image1"],
        [TestAction.recover_image, "image1"],
        [TestAction.expunge_image, "image1"],
        [TestAction.attach_volume, "vm3", "volume3"],
        [TestAction.create_volume_backup, "volume3", "data-backup3"],
        [TestAction.create_mini_vm, "vm4", "data_volume=true", "cpu=2", "memory=2","provisiong=thick"],
        [TestAction.create_volume, "volume4", "=scsi,thick"],
        [TestAction.delete_volume, "volume4"],
        [TestAction.create_mini_vm, "vm5", "data_volume=true", "cpu=random", "memory=2","provisiong=thick"],
        [TestAction.add_image, "image2", 'root', "http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2"],
        [TestAction.expunge_volume, "volume4"],
        [TestAction.change_vm_ha, "vm5"],
        [TestAction.create_volume_backup, "vm5-root", "root-backup5"],
        [TestAction.delete_image, "image2"],
        [TestAction.stop_vm, "vm3"],
        [TestAction.use_volume_backup, "data-backup3"],
        [TestAction.add_image, "image3", 'root', "http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2"],
        [TestAction.create_volume, "volume5", "=scsi,thick"],
        [TestAction.attach_volume, "vm5", "volume5"]
       ])
