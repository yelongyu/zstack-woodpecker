import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", path_list=[
        [TestAction.create_mini_vm, "vm1", 'data_volume=true', 'cpu=random', 'memory=random', 'network=random', 'provisiong=thick'],
        [TestAction.delete_vm, 'vm1'],
        [TestAction.recover_vm, 'vm1'],
        [TestAction.create_vm_by_image, "iso2", "iso", "vm3"],
        [TestAction.add_image, "image1", 'root', "http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2"],
        [TestAction.add_image, "iso2", 'root', os.environ.get('isoForVmUrl')],
        [TestAction.create_volume, "volume1", "=scsi,thick"],
        [TestAction.attach_volume, "vm1", "volume1"],
        [TestAction.create_volume, "volume2", "=scsi,thick"],
        [TestAction.attach_volume, "vm2", "volume2"],
        [TestAction.delete_vm, "vm2"],
        [TestAction.expunge_vm, "vm2"],
        [TestAction.delete_image, "iso2"],
        [TestAction.expunge_image, "iso2"],
        [TestAction.delete_volume, "volume2"],
        [TestAction.expunge_volume, "volume2"],
        [TestAction.change_vm_ha, 'vm1']])