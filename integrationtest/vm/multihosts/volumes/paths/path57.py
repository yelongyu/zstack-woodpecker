import zstackwoodpecker.test_state as ts_header
TestAction = ts_header.TestAction
def path():
    return dict(initial_formation="template2", path_list=[[TestAction.create_volume, "volume1"], [TestAction.attach_volume, "vm1", "volume1"], [TestAction.create_volume, "volume2"], [TestAction.attach_volume, "vm1", "volume2"], [TestAction.create_volume, "volume3"], [TestAction.attach_volume, "vm1", "volume3"], [TestAction.delete_volume, "volume1"], [TestAction.stop_vm, "vm1"], [TestAction.change_vm_image, "vm1"], [TestAction.create_data_vol_template_from_volume, "volume2", "image1"], [TestAction.detach_volume, "volume2"], [TestAction.create_volume_snapshot, "vm1-root", "snapshot1"], [TestAction.start_vm, "vm1"],  [TestAction.resize_data_volume, "volume2", 5*1024*1024], [TestAction.delete_volume, "volume2"], [TestAction.cleanup_ps_cache], [TestAction.detach_volume, "volume3"], [TestAction.ps_migrate_volume, "volume3"], [TestAction.reboot_vm, "vm1"]])