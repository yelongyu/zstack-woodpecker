import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():
    return dict(initial_formation="template2", path_list=[
        [TestAction.add_image, "ImageStoreBackupStorage", "image1", "raw", "RootVolumeTemplate", "FTP"],
        [TestAction.create_vm_by_image, "image1", "qcow2", "vm1"],
        [TestAction.stop_vm, "vm1"],
        [TestAction.delete_image, "image1"],
        [TestAction.expunge_image, "image1"],
        [TestAction.ps_migrate_volume, "vm1-root"],
        [TestAction.start_vm, "vm1"]])

