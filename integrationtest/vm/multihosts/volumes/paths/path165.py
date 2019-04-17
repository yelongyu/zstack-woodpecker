import zstackwoodpecker.test_state as ts_header
TestAction = ts_header.TestAction
def path():
        return dict(initial_formation="template2",
                path_list=[[TestAction.create_data_volume_from_image, "volume1", "=scsi"], \
                [TestAction.attach_volume, "vm1", "volume1"], \
                [TestAction.detach_volume, "volume1"], \
                [TestAction.create_image_from_volume, "vm1", "image1"], \
                [TestAction.attach_volume, "vm1", "volume1"], \
                [TestAction.create_volume_backup, "volume1", "backup1"], \
                [TestAction.detach_volume, "volume1"], \
                [TestAction.clone_vm, "vm1", "vm2", "=full"], \
                [TestAction.use_volume_backup, "backup1"], \
                [TestAction.create_volume_snapshot, "volume1", "snapshot1"], \
                [TestAction.create_volume_snapshot, "volume1", "snapshot2"], \
                [TestAction.create_volume_snapshot, "volume1", "snapshot3"], \
                [TestAction.batch_delete_volume_snapshot, ["snapshot1","snapshot2"]], \
                [TestAction.attach_volume, "vm1", "volume1"], \
                [TestAction.reboot_vm, "vm1"], \
                [TestAction.create_volume_snapshot, "volume1", "snapshot4"], \
                [TestAction.delete_volume_snapshot, "snapshot4"], \
                [TestAction.reboot_vm, "vm1"]])
