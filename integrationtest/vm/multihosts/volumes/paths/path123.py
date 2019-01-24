import zstackwoodpecker.test_state as ts_header
TestAction = ts_header.TestAction
def path():
        return dict(initial_formation="template2",
                path_list=[[TestAction.create_volume, "volume1","=scsi,shareable"], \
                [TestAction.attach_volume, "vm1", "volume1"], \
                [TestAction.create_volume_snapshot, "vm1-root", "snapshot1"], \
                [TestAction.create_volume, "volume4","=scsi"], \
                [TestAction.attach_volume, "vm1", "volume4"], \
                [TestAction.create_volume_backup, "volume4", "backup1"], \
                [TestAction.delete_volume, "volume1"], \
                [TestAction.stop_vm, "vm1"], \
                [TestAction.use_volume_snapshot, "snapshot1"], \
                [TestAction.create_volume, "volume2", "=scsi,shareable"], \
                [TestAction.create_volume_snapshot, "volume2", 'snapshot2'], \
                [TestAction.delete_volume, "volume2"], \
                [TestAction.create_image_from_volume, "vm1", "image1"], \
                [TestAction.create_volume, "volume3", "=scsi,shareable"], \
                [TestAction.create_volume_snapshot, "volume3", "snapshot3"], \
                [TestAction.use_volume_snapshot, "snapshot3"], \
                [TestAction.start_vm, "vm1"], \
                [TestAction.reboot_vm, "vm1"]])

