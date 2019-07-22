import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(repeat=1, initial_formation="template5", path_list=[
        [TestAction.create_mini_vm, "vm1", 'data_volume=false', 'cpu=2', 'memory=2', 'provisiong=thin'],
        [TestAction.create_volume, "volume1", "=scsi,thin"],
        [TestAction.attach_volume, "vm1", "volume1"],
        [TestAction.create_mini_vm, "vm2", 'data_volume=false', 'cpu=2', 'memory=2', 'provisiong=thick'],
        [TestAction.create_volume, "volume2", "=scsi,thick"],
        [TestAction.attach_volume, "vm2", "volume2"],
        [TestAction.change_vm_ha, "vm1"],
        [TestAction.change_vm_ha, "vm2"]] + [[TestAction.run_host_workloads, "all", "fio -filename=/root/fio-test -direct=1 -iodepth 32 -thread -rw=randrw -rwmixread=70 -ioengine=libaio -bs=4k -size=10G -numjobs=8 -runtime=600 -group_reporting -name=fio_test.txt", "background"], [TestAction.idel, "300"], [TestAction.reboot_host, "all", "soft_crash"]]*5000)