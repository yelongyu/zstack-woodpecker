import zstackwoodpecker.test_state as ts_header
TestAction = ts_header.TestAction
def path():
    return dict(initial_formation="template2",\
                path_list=[[TestAction.create_volume, "volume1"], \
                [TestAction.create_volume, "volume3"], \
                [TestAction.attach_volume, "vm1", "volume1"], \
                [TestAction.attach_volume, "vm1", "volume3"], \
                [TestAction.stop_vm, "vm1"], \
		[TestAction.cleanup_ps_cache], \
		[TestAction.start_vm, "vm1"], \
		[TestAction.create_volume_backup, "volume1", "backup1"], \
		[TestAction.delete_volume, "volume3"], \
		[TestAction.create_volume_snapshot, "vm1-root", 'snapshot1'], \
		[TestAction.stop_vm, "vm1"], \
		[TestAction.use_volume_backup, "backup1"], \
		[TestAction.create_volume, "volume2"], \
		[TestAction.create_volume_snapshot, "volume2", "snapshot2"], \
		[TestAction.create_volume_snapshot, "volume2", "snapshot3"], \
		[TestAction.create_volume_snapshot, "volume2", "snapshot4"], \
		[TestAction.batch_delete_volume_snapshot, ["snapshot3", "snapshot4"]], \
		[TestAction.attach_volume, "vm1", "volume2"], \
		[TestAction.start_vm, "vm1"], \
		[TestAction.create_volume_backup, "volume2", "backup2"], \
		[TestAction.stop_vm, "vm1"], \
		[TestAction.use_volume_snapshot, "snapshot1"], \
		[TestAction.use_volume_backup, "backup2"], \
		[TestAction.batch_delete_volume_snapshot, ["snapshot2"]], \
		[TestAction.start_vm, "vm1"], \
		[TestAction.reboot_vm, "vm1"]])
