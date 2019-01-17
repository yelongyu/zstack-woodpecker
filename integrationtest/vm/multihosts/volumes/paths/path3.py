import zstackwoodpecker.test_state as ts_header
TestAction = ts_header.TestAction
def path():
    return dict(initial_formation="template2", path_list=[[TestAction.create_data_volume_from_image, "volume1", "=scsi,shareable"], [TestAction.attach_volume, "vm1", "volume1"], [TestAction.reboot_vm, "vm1"], [TestAction.create_volume_backup, "vm1-root", "backup1"], [TestAction.detach_volume, "volume1"], [TestAction.create_image_from_volume, "vm1", "image1"], [TestAction.create_data_vol_template_from_volume, "volume1", "image2"], [TestAction.delete_volume, "volume1"], [TestAction.clone_vm, "vm1", "vm2", "=full"], [TestAction.create_data_volume_from_image, "volume2", "=scsi,shareable"], [TestAction.ps_migrate_volume, "volume2"], [TestAction.reboot_vm, "vm1"]])

