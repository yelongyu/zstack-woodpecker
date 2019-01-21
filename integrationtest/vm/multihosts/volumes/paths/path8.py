import zstackwoodpecker.test_state as ts_header
TestAction = ts_header.TestAction
def path():
    return dict(initial_formation="template2", path_list=[[TestAction.create_data_volume_from_image, "volume1", "=scsi"], [TestAction.attach_volume, "vm1", "volume1"], [TestAction.stop_vm, "vm1"], [TestAction.change_vm_image, "vm1"], [TestAction.resize_data_volume, "volume1", 5*1024*1024], [TestAction.create_data_volume_from_image, "volume2", "=scsi"], [TestAction.attach_volume, "vm1", "volume2"], [TestAction.clone_vm, "vm1", "vm2", "=full"], [TestAction.start_vm, "vm1"], [TestAction.create_volume_backup, "volume1", "backup1"], [TestAction.delete_volume, "volume2"], [TestAction.migrate_vm, "vm1"], [TestAction.create_volume_snapshot, "volume1", "snapshot1"], [TestAction.reboot_vm, "vm1"]])
