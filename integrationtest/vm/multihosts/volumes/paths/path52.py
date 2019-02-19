import zstackwoodpecker.test_state as ts_header
TestAction = ts_header.TestAction
def path():
    return dict(initial_formation="template2", path_list=[[TestAction.create_volume, "volume1", "=scsi,shareable"], [TestAction.create_volume, "volume2", "=scsi,shareable"], [TestAction.detach_volume, "volume1", "vm1"], [TestAction.create_image_from_volume, "vm1", "image1"], [TestAction.create_data_vol_template_from_volume, "volume1", "image2"], [TestAction.attach_volume, "vm1", "volume2"], [TestAction.cleanup_ps_cache], [TestAction.ps_migrate_volume, "volume1"], [TestAction.delete_volume, "volume1"], [TestAction.reinit_vm, "vm1"], [TestAction.create_data_vol_template_from_volume, "volume2", "image2"], [TestAction.reboot_vm, "vm1"]])
