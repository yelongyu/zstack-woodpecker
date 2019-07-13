import zstackwoodpecker.test_state as ts_header
TestAction = ts_header.TestAction
def path():
    return dict(initial_formation="template5", path_list=[
        [TestAction.create_vm_by_image, "iso1", "iso", "vm1"],
        [TestAction.create_vm_backup, "vm1", "backup1"],
        [TestAction.create_mini_vm, "vm2", 'data_volume=false', 'cpu=random', 'memory=2', 'provisiong=thin'],
        [TestAction.create_volume, "volume1", "=scsi,thin"],
        [TestAction.resize_data_volume, "volume1", 5 * 1024 * 1024],
        [TestAction.attach_volume, "vm1", "volume1"],
        [TestAction.detach_volume, "volume1"],
        [TestAction.create_mini_vm, "vm3", 'data_volume=false', 'cpu=random', 'memory=2', 'network=random',
         'provisiong=thick'],
        [TestAction.delete_volume, "volume1"],
        [TestAction.add_image, "image1", 'root', "http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2"],
        [TestAction.create_volume, "volume2", "size=random", "flag=scsi,thin"],
        [TestAction.attach_volume, "vm2", "volume2"],
        [TestAction.create_volume_backup, "volume2", "backup2"],
        [TestAction.delete_volume_backup, "backup2"],
        [TestAction.delete_image, "image1"],
        [TestAction.recover_image, "image1"],
        [TestAction.delete_image, "image1"],
        [TestAction.expunge_image, "image1"],
        [TestAction.create_vm_backup, "vm1", "backup3"],
        [TestAction.create_vm_backup, "vm2", "backup4"],
        [TestAction.create_mini_vm, "vm3", 'data_volume=true', 'cpu=random', 'memory=2', 'provisiong=thick'],
        [TestAction.create_image_from_volume, "vm1", "vm1-image1"],
        [TestAction.create_image_from_volume, "vm2", "vm2-image1"],
        [TestAction.create_image_from_volume, "vm3", "vm3-image1"],
        [TestAction.create_volume, "volume3", "size=random", "flag=scsi,thin"],
        [TestAction.attach_volume, "vm3", "volume3"],
        [TestAction.delete_volume, "volume3"],
        [TestAction.recover_volume, "volume3"],
        [TestAction.stop_vm, "vm3"],
        [TestAction.add_image, "image2", 'root', "http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2"],
        [TestAction.expunge_volume, "volume1"],
        [TestAction.create_mini_vm, "vm4", 'data_volume=false', 'cpu=random', 'memory=2', 'provisiong=thick'],
        [TestAction.create_vm_backup, "vm1", "backup4"],
        [TestAction.create_vm_backup, "vm2", "backup5"],
        [TestAction.create_vm_backup, "vm4", "backup6"],
        [TestAction.resize_data_volume, "volume2", 5 * 1024 * 1024],
        [TestAction.resize_data_volume, "volume3", 5 * 1024 * 1024],
        [TestAction.stop_vm, "vm1"],
        [TestAction.stop_vm, "vm2"],
        [TestAction.stop_vm, "vm4"],
        [TestAction.use_vm_backup, "backup1"],
        [TestAction.use_vm_backup, "backup5"],
        [TestAction.use_vm_backup, "backup4"],
        [TestAction.use_vm_backup, "backup6"],
        [TestAction.start_vm, "vm1"],
        [TestAction.start_vm, "vm2"],
        [TestAction.start_vm, "vm4"],
        [TestAction.add_image, "image3", 'root', "http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2"],
        [TestAction.create_volume, "volume4", "size=random", "flag=scsi,thin"]])
