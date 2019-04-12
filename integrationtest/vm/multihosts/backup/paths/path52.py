import zstackwoodpecker.test_state as ts_header

TestAction = ts_header.TestAction
def path():
    return dict(initial_formation="template2",
        path_list=[[TestAction.create_volume, "volume1", "=scsi"],\
        [TestAction.attach_volume, "vm1", "volume1"], \
        [TestAction.create_volume_backup, "vm1-root", "backup1"], \
	[TestAction.create_volume_backup, "vm1-root", "backup2"], \
	[TestAction.migrate_vm, "vm1"], \
	[TestAction.stop_vm, "vm1"], \
        [TestAction.use_volume_backup, "backup1"], \
        [TestAction.start_vm, "vm1"], \
	[TestAction.migrate_vm, "vm1"], \
	[TestAction.create_volume_backup, "volume1", "backup3"], \
	[TestAction.stop_vm, "vm1"], \
        [TestAction.use_volume_backup, "backup2"], \
        [TestAction.start_vm, "vm1"], \
	[TestAction.create_volume_snapshot, "volume1", "snapshot62"], \
        [TestAction.create_volume_snapshot, "volume1", "snapshot63"], \
	[TestAction.batch_delete_volume_snapshot, ["snapshot62"]], \
	[TestAction.create_volume_snapshot, "volume1", "snapshot64"], \
	[TestAction.create_vm_backup, "vm1", "backup4"], \
	[TestAction.stop_vm, "vm1"], \
        [TestAction.use_vm_backup, "backup4"], \
        [TestAction.start_vm, "vm1"]])
