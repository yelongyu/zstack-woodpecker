import zstackwoodpecker.test_state as ts_header
TestAction = ts_header.TestAction
def path():
    return dict(initial_formation="template2", 
                path_list=[[TestAction.create_volume, "volume1", "=scsi"],
                           [TestAction.attach_volume, "vm1", "volume1"],
                           [TestAction.create_volume, "volume2", "=scsi"],
                           [TestAction.attach_volume, "vm1", "volume2"],
                           [TestAction.detach_volume, "volume1"],
                           [TestAction.create_image_from_volume, "vm1", "image1"],
                           [TestAction.create_data_vol_template_from_volume, "volume1", "image2"],
                           [TestAction.detach_volume, "volume2"],
                           [TestAction.create_volume_snapshot, "vm1-root", "snapshot1"],
                           [TestAction.create_data_vol_template_from_volume, "volume2", "image3"],
                           [TestAction.attach_volume, "vm1", "volume1"],
                           [TestAction.stop_vm, "vm1"],
                           [TestAction.use_volume_snapshot, "snapshot1"],
                           [TestAction.create_volume_snapshot, "volume1", "snapshot2"],
                           [TestAction.delete_volume_snapshot, "snapshot2"],
                           [TestAction.start_vm, "vm1"],
                           [TestAction.reboot_vm, "vm1"]])
