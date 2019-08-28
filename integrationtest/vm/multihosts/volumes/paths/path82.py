import zstackwoodpecker.test_state as ts_header
TestAction = ts_header.TestAction
def path():
    return dict(initial_formation="template2",
        path_list=[[TestAction.create_volume, "volume1", "=scsi,shareable"],
	[TestAction.attach_volume, "vm1", "volume1"],
	[TestAction.detach_volume, "volume1", "vm1"],
	[TestAction.migrate_vm, "vm1"],
	[TestAction.migrate_vm, "vm1"],
	# [TestAction.create_volume_snapshot, "volume1", 'snapshot1'],
	[TestAction.attach_volume, "vm1", "volume1"],
	[TestAction.migrate_vm, "vm1"],
	[TestAction.migrate_vm, "vm1"],
	# [TestAction.use_volume_snapshot, "snapshot1"],
	[TestAction.delete_volume, "volume1"],
	[TestAction.clone_vm, "vm1", "vm2", "full"],
	[TestAction.create_volume, "volume2", "=scsi"],
	[TestAction.attach_volume, "vm1", "volume2"],
	[TestAction.create_volume_backup, "volume2", "backup1"],
	[TestAction.reboot_vm, "vm1"]])
