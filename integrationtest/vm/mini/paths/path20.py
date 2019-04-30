import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():
    return dict(initial_formation="template5", path_list=[
        [TestAction.create_mini_vm, "vm1", 'data_volume=true', 'cpu=2', 'memory=2', 'provisiong=thick'],
        [TestAction.create_volume_backup, "vm1-root", "backup1"],
        [TestAction.stop_vm, "vm1"],
        [TestAction.create_volume, "volume1", "=scsi,thin"],
        [TestAction.attach_volume, "vm1", "volume1"],
        [TestAction.detach_volume, "volume1"],
        [TestAction.create_mini_vm, "vm2", 'data_volume=false', 'cpu=2', 'memory=2', 'network=random',
         'provisiong=thin'],
        [TestAction.delete_volume, "volume1"],
        [TestAction.recover_volume, "volume1"],
        [TestAction.add_image, "image1", 'root', "http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2"],
        [TestAction.delete_volume_backup, "backup1"],
        [TestAction.delete_image, "image1"],
        [TestAction.expunge_image, "image1"],
        [TestAction.attach_volume, "vm2", "volume1"],
        [TestAction.create_volume_backup, "volume1", "backup2"],
        [TestAction.add_image, "iso1", 'root', os.environ.get('isoForVmUrl')],
        [TestAction.create_vm_by_image, "iso1", "iso", "vm3"],
        [TestAction.create_volume, "volume2", "=scsi,thin"],
        [TestAction.delete_volume, "volume2"],
        [TestAction.recover_volume, "volume2"],
        [TestAction.create_mini_vm, "vm1", 'data_volume=true', 'cpu=2', 'memory=random', 'provisiong=thick'],
        [TestAction.add_image, "image2", 'root', "http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2"],
        [TestAction.delete_volume, "volume1"],
        [TestAction.expunge_volume, "volume1"],
        [TestAction.reboot_vm, "vm2"],
        [TestAction.reboot_vm, "vm3"],
        [TestAction.create_volume_backup, "vm2-root", "backup3"],
        [TestAction.delete_image, "iso1"],
        [TestAction.delete_volume_backup, "backup2"],
        [TestAction.add_image, "image3", 'root', "http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2"],
        [TestAction.detach_volume, "volume2"]])

