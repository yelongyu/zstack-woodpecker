import zstackwoodpecker.test_state as ts_header
TestAction = ts_header.TestAction
def path():
    return dict(initial_formation="template1", 
           path_list=[
                      [TestAction.add_image, "ImageStoreBackupStorage", "image1", "iso", "RootVolumeTemplate", "FTP"], 
                      [TestAction.add_image, "ImageStoreBackupStorage", "data-img1", "iso", "DataVolumeTemplate", "FTP"], 
                      [TestAction.create_vm_by_image, "image1", "iso", "vm1"], 
                      [TestAction.create_data_volume_from_image, "volume1", "data-img1"], 
                      [TestAction.ps_migrage_vm, "vm1"], 
                      [TestAction.sync_image_from_imagestore, "image1"], 
                      [TestAction.create_volume_snapshot, "volume1", 'snapshot1'], 
                      [TestAction.create_data_volume_from_image, "volume2", "data-img1"], 
                      [TestAction.reclaim_space_from_bs], 
                      [TestAction.delete_image, "image1"],
                      [TestAction.migrate_vm, "vm1"],
                      
                     ])
