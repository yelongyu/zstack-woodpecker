import zstackwoodpecker.test_state as ts_header
TestAction = ts_header.TestAction
def path():
    return dict(initial_formation="template1", path_list=[[TestAction.detach_volume, "vm1-volume1"], [TestAction.reboot_vm, "vm1"], [TestAction.create_volume_snapshot, "vm1-volume2", "snapshot1"], [TestAction.delete_volume, "vm1-volume3"], [TestAction.stop_vm, "vm1"], [TestAction.change_vm_image, "vm1"], [TestAction.use_volume_snapshot, "snapshot1"], [TestAction.start_vm, "vm1"], [TestAction.attach_volume, "vm1", "vm1-volume1"], [TestAction.reboot_vm, "vm1"], [TestAction.create_data_vol_template_from_volume, "vm1-volume1", "image1"], [TestAction.reboot_vm, "vm1"]])
