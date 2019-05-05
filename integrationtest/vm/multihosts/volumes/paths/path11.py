import zstackwoodpecker.test_state as ts_header
TestAction = ts_header.TestAction
def path():
    return dict(initial_formation="template2", path_list=[[TestAction.create_data_volume_from_image, "volume1", "=scsi"], [TestAction.create_data_volume_from_image, "volume2", "=scsi"], [TestAction.attach_volume, "vm1", "volume1"], [TestAction.detach_volume, "volume1"], [TestAction.create_image_from_volume, "vm1", "image1"], [TestAction.attach_volume, "vm1", "volume1"], [TestAction.create_volume_backup, "volume1", "backup1"], [TestAction.delete_volume, "volume1"], [TestAction.stop_vm, "vm1"], [TestAction.ps_migrate_volume, "vm1-root"], [TestAction.start_vm, "vm1"], [TestAction.create_volume_snapshot, "volume2", "snapshot1"], [TestAction.create_volume_snapshot, "volume2", "snapshot2"], [TestAction.create_volume_snapshot, "volume2", "snapshot3"], [TestAction.delete_volume_snapshot, "snapshot1"], [TestAction.delete_volume, "volume2"], [TestAction.cleanup_ps_cache], [TestAction.resize_data_volume, "volume2", 5*1024*1024], [TestAction.create_volume_snapshot, "vm1-root", "snapshot4"], [TestAction.create_volume_snapshot, "vm1-root", "snapshot5"], [TestAction.create_volume_snapshot, "vm1-root", "snapshot6"], [TestAction.batch_delete_volume_snapshot, ["snapshot4", "snapshot5", "snapshot6"]], [TestAction.reboot_vm, "vm1"]])