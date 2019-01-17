import zstackwoodpecker.test_state as ts_header
TestAction = ts_header.TestAction
def path():
    return dict(initial_formation="template1", path_list=[[TestAction.stop_vm, "vm1"], [TestAction.start_vm, "vm1"], [TestAction.delete_volume, "vm1-volume1"], [TestAction.create_image_from_volume, "vm1", "image1"], [TestAction.resize_volume, "vm1", 5*1024*1024], [TestAction.detach_volume, "vm1-volume2"], [TestAction.stop_vm, "vm1"], [TestAction.reinit_vm, "vm1"], [TestAction.start_vm, "vm1"], [TestAction.resize_volume, "vm1", 5*1024*1024], [TestAction.detach_volume, "vm1-volume3"], [TestAction.stop_vm, "vm1"], [TestAction.change_vm_image, "vm1"], [TestAction.start_vm, "vm1"], [TestAction.create_data_vol_template_from_volume, "vm1-volume2", "image2"], [TestAction.reboot_vm, "vm1"]])

