import zstackwoodpecker.test_state as ts_header
TestAction = ts_header.TestAction
def path():
    return dict(initial_formation="template1", 
           path_list=[
                      [TestAction.add_image, "ImageStoreBackupStorage", "image1", "raw", "RootVolumeTemplate", "HTTPS"], 
                      [TestAction.add_image, "ImageStoreBackupStorage", "data-img1", "raw", "DataVolumeTemplate", "HTTPS"], 
                      [TestAction.create_vm_by_image, "image1", "raw", "vm1"], 
                      [TestAction.create_data_volume_from_image, "volume1", "data-img1"], 
                      [TestAction.stop_vm, "vm1"], 
                      [TestAction.change_vm_image, "vm1"],
                      [TestAction.export_image, "image1"],
                      [TestAction.attach_volume, "vm1", "volume1"],
                      [TestAction.detach_volume, "volume1", "vm1"],
                      [TestAction.delete_volume, "volume1"],
                      [TestAction.create_vm_by_image, "image1", "raw", "vm2"], 
                      [TestAction.reconnect_bs], 
                      [TestAction.create_data_vol_template_from_volume, "volume1", "data-img2"]
                      [TestAction.reclaim_space_from_bs], 
                      [TestAction.start_vm, "vm1"]
                     ])
