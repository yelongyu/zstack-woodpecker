import zstackwoodpecker.test_state as ts_header
TestAction = ts_header.TestAction
def path():
    return dict(initial_formation="template1", \
           path_list=[
                      [TestAction.add_image, "ImageStoreBackupStorage", "image1", "raw", "RootVolumeTemplate", "HTTPS"], \
                      [TestAction.add_image, "ImageStoreBackupStorage", "data-img1", "raw", "DataVolumeTemplate", "HTTPS"], \
                      [TestAction.create_vm_by_image, "image1", "raw", "vm1"], \
                      [TestAction.create_data_volume_from_image, "volume1", "data-img1"], \
                      [TestAction.stop_vm, "vm1"], \
                      [TestAction.start_vm, "vm1"]
                     ])
