import zstackwoodpecker.test_state as ts_header
TestAction = ts_header.TestAction
def path():
    return dict(initial_formation="template2", 
                path_list=[[TestAction.create_data_volume_from_image, "volume1", "=scsi"],
                           [TestAction.create_data_volume_from_image, "volume2", "=scsi"],
                           [TestAction.attach_volume, "vm1", "volume1"],
                           [TestAction.create_volume_snapshot, "vm1-root", "snapshot1"],
                           [TestAction.detach_volume, "volume1"],
                           [TestAction.ps_migrate_volume, "volume1"],
                           [TestAction.stop_vm, "vm1"],
                           [TestAction.attach_volume, "vm1", "volume2"],
                           [TestAction.detach_volume, "volume2"],
                           [TestAction.ps_migrate_volume, "vm1-root"],
                           [TestAction.resize_data_volume, "volume2", 5*1024*1024],
                           [TestAction.start_vm, "vm1"],
                           [TestAction.attach_volume, "vm1", "volume1"],
                           [TestAction.stop_vm, "vm1"],
                           [TestAction.use_volume_snapshot, "snapshot1"],
                           [TestAction.ps_migrate_volume, "volume2"],
                           [TestAction.start_vm, "vm1"],
                           [TestAction.reboot_vm, "vm1"]
                          ]
               )
