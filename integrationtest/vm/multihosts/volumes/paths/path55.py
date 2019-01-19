import zstackwoodpecker.test_state as ts_header
TestAction = ts_header.TestAction
def path():
    return dict(initial_formation="template5", path_list=[[TestAction.create_volume, "volume1"], [TestAction.attach_volume, "vm1", "volume1"], [TestAction.create_volume_snapshot, "vm1-root", "snapshot1"], [TestAction.resize_data_volume, "vm1-volume1", 5*1024*1024], [TestAction.delete_volume, "vm1-volume2"], [TestAction.stop_vm, "vm1"], [TestAction.use_volume_snapshot, "snapshot1"], [TestAction.create_volume_snapshot, "volume1", "snapshot2"], [TestAction.attach_volume, "vm1", "volume2"], [TestAction.attach_volume, "vm1", "volume2"], [TestAction.create_volume_snapshot, "vm1-root", "snapshot3"], [TestAction.use_volume_snapshot, "snapshot2"], [TestAction.reboot_vm, "vm1"]])
