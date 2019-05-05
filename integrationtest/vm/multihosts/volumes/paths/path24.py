import zstackwoodpecker.test_state as ts_header
TestAction = ts_header.TestAction
def path():
    return dict(initial_formation="template2", 
                path_list=[[TestAction.create_volume, "volume1", "=scsi"], 
                           [TestAction.attach_volume, "vm1", "volume1"], 
                           [TestAction.create_volume, "volume2", "=scsi"], 
                           [TestAction.attach_volume, "vm1", "volume2"], 
                           [TestAction.detach_volume, "volume1"], 
                           [TestAction.cleanup_ps_cache], 
                           [TestAction.attach_volume, "vm1", "volume1"], 
                           [TestAction.create_volume_backup, "volume1", "backup1"], 
                           [TestAction.delete_volume, "volume1"], 
                           [TestAction.cleanup_ps_cache], 
                           [TestAction.create_data_template_from_backup, "backup1", "image1"], 
                           [TestAction.create_data_volume_from_image, "volume3", "image1", "=scsi"], 
                           [TestAction.create_volume_snapshot, "volume2", "snapshot2"],
                           [TestAction.delete_volume_snapshot, "snapshot2"], 
                           [TestAction.delete_volume, "volume3"], 
                           [TestAction.create_volume_snapshot, "vm1-root", "snapshot1-1"], 
                           [TestAction.create_volume_snapshot, "vm1-root", "snapshot1-2"], 
                           [TestAction.create_volume_snapshot, "vm1-root", "snapshot1-3"], 
                           [TestAction.create_volume_snapshot, "vm1-root", "snapshot1-4"], 
                           [TestAction.batch_delete_volume_snapshot, ["snapshot1-3","snapshot1-1","snapshot1-2"]], 
                           [TestAction.create_volume_backup, "volume2", "backup2"], 
                           [TestAction.reboot_vm, "vm1"]])