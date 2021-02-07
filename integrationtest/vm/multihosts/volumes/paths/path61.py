import zstackwoodpecker.test_state as ts_header

TestAction = ts_header.TestAction


def path():
    return dict(initial_formation="template2", faild_point=13,
                path_list=[[TestAction.create_volume, "volume1"], [TestAction.attach_volume, "vm1", "volume1"],
                           [TestAction.create_volume, "volume2"], [TestAction.create_volume, "volume3"],
                           [TestAction.delete_volume, "volume1"], [TestAction.stop_vm, "vm1"],
                           [TestAction.reinit_vm, "vm1"], [TestAction.start_vm, "vm1"],
                           [TestAction.create_vm_backup, "vm1", "backup1"], [TestAction.delete_volume, "volume2"],
                           [TestAction.create_volume_snapshot, "volume3", "snapshot1"], [TestAction.stop_vm, "vm1"],
                           [TestAction.use_vm_backup, "backup1"], [TestAction.attach_volume, "vm1", "volume3"],
                           [TestAction.clone_vm, "vm1", "vm2"], [TestAction.use_vm_backup, "backup1"],
                           [TestAction.start_vm, "vm1"], [TestAction.reboot_vm, "vm1"]])
