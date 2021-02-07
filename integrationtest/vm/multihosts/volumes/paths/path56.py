import zstackwoodpecker.test_state as ts_header

TestAction = ts_header.TestAction


def path():
    return dict(initial_formation="template2", faild_point=22, path_list=[
        [TestAction.create_volume, "volume1", "=scsi"],
        [TestAction.create_volume, "volume2", "=scsi"],
        [TestAction.attach_volume, "vm1", "volume2"],
        [TestAction.create_volume, "volume3", "=scsi"],
        [TestAction.attach_volume, "vm1", "volume3"],
        [TestAction.create_volume, "volume4", "=scsi"],
        [TestAction.attach_volume, "vm1", "volume4"],
        [TestAction.create_volume, "volume5", "=scsi"],
        [TestAction.attach_volume, "vm1", "volume5"],
        [TestAction.create_volume, "volume6", "=scsi"],
        [TestAction.attach_volume, "vm1", "volume6"],
        [TestAction.create_volume, "volume7", "=scsi"],
        [TestAction.attach_volume, "vm1", "volume7"],
        [TestAction.create_volume, "volume8", "=scsi"],
        [TestAction.attach_volume, "vm1", "volume8"],
        [TestAction.create_volume_snapshot, "vm1-root", "snapshot1"],
        [TestAction.create_vm_backup, "vm1", "backup1"],
        [TestAction.create_volume, "volume9", "=scsi"],
        [TestAction.attach_volume, "vm1", "volume9"],
        [TestAction.stop_vm, "vm1"],
        [TestAction.use_volume_snapshot, "snapshot1"],
        [TestAction.use_vm_backup, "backup1"],
        [TestAction.delete_volume, "volume9"],
        [TestAction.use_volume_snapshot, "snapshot1"],
        [TestAction.start_vm, "vm1"],
        [TestAction.create_data_vol_template_from_volume, "volume2", "image1"],
        [TestAction.reboot_vm, "vm1"]])
