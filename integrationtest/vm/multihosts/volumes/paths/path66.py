import zstackwoodpecker.test_state as ts_header
TestAction = ts_header.TestAction
def path():
    return dict(initial_formation="template3", path_list=[[TestAction.create_volume, "volume2"], [TestAction.create_volume, "volume3"], [TestAction.detach_volume, "vm1-volume1"], [TestAction.clone_vm, "vm1", "vm2"], [TestAction.stop_vm, "vm1"], [TestAction.ps_migrate_volume, "vm1-volume1"], [TestAction.ps_migrate_volume, "vm1-root"], [TestAction.attach_volume, "vm1", "vm1-volume1"], [TestAction.cleanup_ps_cache], [TestAction.create_volume_snapshot, "vm1-volume1", "snapshot1"], [TestAction.ps_migrate_volume, "volume2"], [TestAction.attach_volume, "vm1", "volume2"], [TestAction.reinit_vm, "vm1"], [TestAction.use_volume_snapshot, "snapshot1"], [TestAction.reboot_vm, "vm1"]])
