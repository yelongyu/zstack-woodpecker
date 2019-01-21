import zstackwoodpecker.test_state as ts_header
TestAction = ts_header.TestAction
def path():
    return dict(initial_formation="template2", path_list=[[TestAction.create_volume, "volume1"], [TestAction.attach_volume, "vm1", "volume1"], [TestAction.create_image_from_volume, "vm1", "image1"], [TestAction.create_volume_snapshot, "volume1", "snapshot1"], [TestAction.delete_volume, "volume1"], [TestAction.ps_migrate_volume, "vm1-root"], [TestAction.use_volume_snapshot, "snapshot1"], [TestAction.ps_migrate_volume, "volume1"], [TestAction.attach_volume, "vm1", "volume1"], [TestAction.detach_volume, "volume1"], [TestAction.create_image_from_volume, "vm1", "image2"], [TestAction.create_volume_snapshot, "volume1", "snapshot2"], [TestAction.reboot_vm, "vm1"]])
