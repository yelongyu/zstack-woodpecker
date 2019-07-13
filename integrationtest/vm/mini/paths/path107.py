import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(repeat=1, initial_formation="template5", path_list=[
        [TestAction.create_mini_vm, "vm1", 'data_volume=false', 'cpu=2', 'memory=2', 'provisiong=thick'],
        [TestAction.create_volume, "volume1", "size=random", "flag=scsi,thin,large,nocheck"],
        [TestAction.attach_volume, "vm1", "volume1"],
        [TestAction.run_workloads, "target_vms=vm1", "FIO", "fio -filename=/dev/sda -direct=1 -iodepth 32 -thread -rw=randrw -rwmixread=70 -ioengine=libaio -bs=4k -size=90% -numjobs=8 -runtime=3600 -group_reporting -name=fio_test.txt", 60],
        [TestAction.change_vm_ha, "vm1"]] + [[TestAction.idel, "600"], [TestAction.reboot_host, "all", "soft_crash"]]*5000)
