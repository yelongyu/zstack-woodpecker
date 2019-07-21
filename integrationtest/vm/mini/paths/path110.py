import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(repeat=1, initial_formation="template5", path_list=[
        [TestAction.create_mini_vm, "vm1", 'data_volume=false', 'cpu=2', 'memory=2', 'provisiong=thin', 'network=public network'],
        [TestAction.create_volume, "volume1", "=scsi,thin"],
        [TestAction.attach_volume, "vm1", "volume1"],
        [TestAction.create_mini_vm, "vm2", 'data_volume=false', 'cpu=2', 'memory=2', 'provisiong=thick', 'network=public network'],
        [TestAction.create_volume, "volume2", "=scsi,thick"],
        [TestAction.attach_volume, "vm2", "volume2"],
        [TestAction.change_vm_ha, "vm1"],
        [TestAction.change_vm_ha, "vm2"],
	[TestAction.run_workloads, "target_vms=vm1", "IPERF", "iperf3 -s", 60]] + [[TestAction.run_host_workloads, "random", "iperf3 -c vm1 -t 600", "background"], [TestAction.idel, "300"], [TestAction.reboot_host, "all", "soft_crash"]]*5000)
