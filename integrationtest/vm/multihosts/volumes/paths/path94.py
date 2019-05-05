import zstackwoodpecker.test_state as ts_header
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template2", path_list=[
	[TestAction.create_volume, "volume1"],
	[TestAction.attach_volume, "vm1", "volume1"],
	[TestAction.reboot_vm, "vm1"],
	[TestAction.create_volume_snapshot, "volume1", "snapshot1"],
	[TestAction.detach_volume, "volume1"],
        [TestAction.stop_vm, "vm1"],
        [TestAction.ps_migrate_volume, "vm1-root"],
        [TestAction.start_vm, "vm1"],
	[TestAction.use_volume_snapshot, "snapshot1"],
        [TestAction.ps_migrate_volume, "volume1"],
	[TestAction.attach_volume, "vm1", "volume1"],
	[TestAction.create_volume_backup, "volume1", "backup1"],
	[TestAction.delete_volume, "volume1"],
	[TestAction.migrate_vm, "vm1"],

	[TestAction.reboot_vm, "vm1"]])