import zstackwoodpecker.test_state as ts_header
TestAction = ts_header.TestAction
def path():
        return dict(initial_formation="template2",
                path_list=[[TestAction.create_volume, "volume1", "=scsi"], \
                [TestAction.attach_volume, "vm1", "volume1"], \
                [TestAction.create_image_from_volume, "vm1", "image1"], \
                [TestAction.create_volume_backup, "volume1", "backup1"], \
                [TestAction.stop_vm, "vm1"],\
                [TestAction.change_vm_image, "vm1"], \
                [TestAction.start_vm, "vm1"],\
                [TestAction.stop_vm, "vm1"],\
                [TestAction.use_volume_backup, "backup1"], \
                [TestAction.start_vm, "vm1"],\
                [TestAction.create_volume_snapshot, "volume1", "snapshot1"], \
                [TestAction.create_volume_snapshot, "volume1", "snapshot2"], \
                [TestAction.create_volume_snapshot, "volume1", "snapshot3"], \
                [TestAction.delete_volume_snapshot, "snapshot1"], \
                [TestAction.detach_volume, "volume1"], \
                [TestAction.stop_vm, "vm1"],\
                [TestAction.reinit_vm, "vm1"], \
                [TestAction.start_vm, "vm1"],\
                [TestAction.resize_data_volume, "volume1", 5*1024*1024], \
                [TestAction.batch_delete_volume_snapshot, ["snapshot3","snapshot2"]], \
                [TestAction.reboot_vm, "vm1"]])
