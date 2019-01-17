import zstackwoodpecker.test_state as ts_header
TestAction = ts_header.TestAction
def path():
    return dict(initial_formation="template2", path_list=[[TestAction.create_volume, "volume1"], [TestAction.attach_volume, "vm1", "volume1"], [TestAction.create_volume, "volume2"], [TestAction.delete_volume, "volume1"], [TestAction.reboot_vm, "vm1"], [TestAction.create_vm_backup, "vm1", "backup1"], [TestAction.attach_volume, "vm1", "volume2"], [TestAction.stop_vm, "vm1"], [TestAction.change_vm_image, "vm1"], [TestAction.stop_vm, "vm1"], [TestAction.use_vm_backup, "backup1"], [TestAction.delete_volume, "volume2"], [TestAction.reinit_vm, "vm1"], [TestAction.start_vm, "vm1"], [TestAction.create_volume_snapshot, "vm1-root", "snapshot1"], [TestAction.reboot_vm, "vm1"]])
