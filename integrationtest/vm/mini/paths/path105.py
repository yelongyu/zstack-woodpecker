import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(repeat=1, initial_formation="template5", path_list=[
        [TestAction.create_mini_vm, "vm1", 'data_volume=false', 'cpu=2', 'memory=2', 'provisiong=thick'],
        [TestAction.create_volume, "volume1", "=scsi,thin"],
        [TestAction.attach_volume, "vm1", "volume1"],
        [TestAction.change_vm_ha, "vm1"],
        [TestAction.create_mini_vm, "vm2", 'data_volume=false', 'cpu=2', 'memory=2', 'provisiong=thin'],
        [TestAction.change_vm_ha, "vm2"],
        [TestAction.create_volume, "volume2", "=scsi,thick"],
        [TestAction.attach_volume, "vm2", "volume2"]] + [[TestAction.reboot_host, "all", "reboot"]]*5000)

