import zstackwoodpecker.test_state as ts_header

TestAction = ts_header.TestAction


def path():
    return dict(initial_formation="template2",
                path_list=[[TestAction.create_volume, "volume1"], [TestAction.attach_volume, "vm1", "volume1"],
                           [TestAction.create_volume, "volume2"], [TestAction.attach_volume, "vm1", "volume2"],
                           [TestAction.create_volume, "volume3"], [TestAction.create_volume, "volume4"],
                           [TestAction.attach_volume, "vm1", "volume4"], [TestAction.create_volume, "volume5"],
                           [TestAction.attach_volume, "vm1", "volume5"], [TestAction.create_volume, "volume6"],
                           [TestAction.attach_volume, "vm1", "volume6"], [TestAction.create_volume, "volume7"],
                           [TestAction.attach_volume, "vm1", "volume7"], [TestAction.create_volume, "volume8"],
                           [TestAction.detach_volume, "volume1"], [TestAction.cleanup_ps_cache],
                           [TestAction.create_data_vol_template_from_volume, "volume1", "image1"],
                           [TestAction.delete_volume, "volume1"], [TestAction.detach_volume, "volume2"],
                           [TestAction.detach_volume, "volume4"], [TestAction.detach_volume, "volume5"],
                           [TestAction.detach_volume, "volume6"], [TestAction.detach_volume, "volume7"],
                           [TestAction.stop_vm, "vm1"], [TestAction.ps_migrate_volume, "vm1-root"],
                           [TestAction.ps_migrate_volume, "volume2"], [TestAction.start_vm, "vm1"],
                           [TestAction.attach_volume, "vm1", "volume2"],
                           [TestAction.create_vm_backup, "vm1", "backup1"], [TestAction.detach_volume, "volume2"],
                           [TestAction.create_image_from_volume, "vm1", "image2"],
                           [TestAction.ps_migrate_volume, "volume3"], [TestAction.reboot_vm, "vm1"]])
