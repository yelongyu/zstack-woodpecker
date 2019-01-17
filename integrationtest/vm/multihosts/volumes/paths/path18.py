import zstackwoodpecker.test_state as ts_header
TestAction = ts_header.TestAction
def path():
    return dict(initial_formation="template2", path_list=[[TestAction.create_data_volume_from_image, "volume1", "=scsi"], [TestAction.create_data_volume_from_image, "volume2", "=scsi"], [TestAction.create_data_volume_from_image, "volume3", "=scsi"], [TestAction.create_data_volume_from_image, "volume4", "=scsi"], [TestAction.create_data_volume_from_image, "volume5", "=scsi"], [TestAction.create_data_volume_from_image, "volume6", "=scsi"], [TestAction.create_data_volume_from_image, "volume7", "=scsi"], [TestAction.create_data_volume_from_image, "volume8", "=scsi"], [TestAction.attach_volume, "vm1", "volume1"], [TestAction.attach_volume, "vm1", "volume2"], [TestAction.attach_volume, "vm1", "volume3"], [TestAction.attach_volume, "vm1", "volume4"], [TestAction.attach_volume, "vm1", "volume5"], [TestAction.attach_volume, "vm1", "volume6"], [TestAction.attach_volume, "vm1", "volume7"], [TestAction.attach_volume, "vm1", "volume8"], [TestAction.create_data_volume_from_image, "volume9", "=scsi"], [TestAction.delete_volume, "volume1"], [TestAction.stop_vm, "vm1"], [TestAction.reinit_vm, "vm1"], [TestAction.create_volume_snapshot, "volume2", "snapshto1"], [TestAction.attach_volume, "vm1", "volume9"], [TestAction.detach_volume, "volume2"], [TestAction.detach_volume, "volume3"], [TestAction.create_volume_snapshot, "volume3", "snapshot1"], [TestAction.detach_volume, "volume4"], [TestAction.detach_volume, "volume5"], [TestAction.detach_volume, "volume6"], [TestAction.detach_volume, "volume7"], [TestAction.detach_volume, "volume8"], [TestAction.detach_volume, "volume9"], [TestAction.ps_migrate_volume, "vm1-root"], [TestAction.ps_migrate_volume, "volume2"], [TestAction.attach_volume, "vm1", "volume2"], [TestAction.start_vm, "vm1"], [TestAction.create_volume_backup, "volume2", "backup1"], [TestAction.ps_migrate_volume, "volume3"], [TestAction.attach_volume, "vm1", "volume3"], [TestAction.create_image_from_volume, "vm1", "image1"], [TestAction.use_volume_snapshot, "snapshot1"], [TestAction.reboot_vm, "vm1"]])
