import zstackwoodpecker.test_state as ts_header
TestAction = ts_header.TestAction
def path():
    return dict(initial_formation="template1", path_list=[[TestAction.delete_volume, "vm1-volume1"], [TestAction.reinit_vm, "vm1"], [TestAction.create_data_vol_template_from_volume, "vm1-volume2", "image1"], [TestAction.delete_volume, "vm-volume2"], [TestAction.reboot_vm, "vm1"], [TestAction.create_volume_backup, "vm1-volume3", "backup1"], [TestAction.detach_volume, "vm1-volume3"], [TestAction.reinit_vm, "vm1"], [TestAction.ps_migrate_volume, "vm1-volume3"], [TestAction.reboot_vm, "vm1"]])
