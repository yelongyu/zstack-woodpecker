import zstackwoodpecker.test_state as ts_header
TestAction = ts_header.TestAction
def path():
    return dict(initial_formation="template2", \
                path_list=[[TestAction.create_data_volume_from_image, "volume1", "=scsi"], 
                          [TestAction.attach_volume, "vm1", "volume1"], 
                          [TestAction.create_data_volume_from_image, "volume2", "=scsi"],
                          [TestAction.attach_volume, "vm1", "volume2"], 
                          [TestAction.create_data_volume_from_image, "volume3", "=scsi"], 
                          [TestAction.attach_volume, "vm1", "volume3"], 
                          [TestAction.delete_volume, "volume1"], 
                          [TestAction.create_volume_snapshot, "vm1-root", "snapshot1-1"], 
                          [TestAction.create_volume_snapshot, "vm1-root", "snapshot1-2"], 
                          [TestAction.detach_volume, "volume2"], 
                          [TestAction.create_volume_snapshot, "volume2", "snapshot2-1"], 
                          [TestAction.create_volume_snapshot, "volume2", "snapshot2-2"], 
                          [TestAction.create_volume_snapshot, "volume2", "snapshot2-3"], 
                          [TestAction.create_volume_snapshot, "volume2", "snapshot2-4"], 
                          [TestAction.delete_volume, "volume3"], 
                          [TestAction.batch_delete_volume_snapshot, ["snapshot2-2","snapshot2-3"]],
                          [TestAction.reboot_vm, "vm1"], 
                          [TestAction.stop_vm, "vm1"], 
                          [TestAction.use_volume_snapshot, "snapshot2-1"], 
                          [TestAction.attach_volume, "vm1", "volume2"], 
                          [TestAction.use_volume_snapshot, "snapshot1-1"], 
                          [TestAction.use_volume_snapshot, "snapshot2-1"],
                          [TestAction.start_vm, "vm1"], 
                          [TestAction.delete_volume_snapshot, "snapshot2-1"], 
                          [TestAction.reboot_vm, "vm1"]
])
