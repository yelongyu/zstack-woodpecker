import zstackwoodpecker.test_state as ts_header

TestAction = ts_header.TestAction
def path():
    return dict(initial_formation="template2",
        path_list=[[TestAction.create_volume, "volume1", "=scsi"],\
        [TestAction.attach_volume, "vm1", "volume1"], \
        [TestAction.create_volume_backup, "volume1", "backup1"], \
	[TestAction.stop_vm, "vm1"], \
        [TestAction.use_volume_backup, 'backup1'],
        [TestAction.start_vm, "vm1"], \
	[TestAction.cleanup_ps_cache], \
	[TestAction.create_volume_snapshot, "volume1", "snapshot1"], \
        [TestAction.create_volume_snapshot, "volume1", "snapshot2"], \
	[TestAction.delete_volume_snapshot, "snapshot1"], \
	[TestAction.create_vm_backup, "vm1", "backup2"], \
	[TestAction.stop_vm, "vm1"], \
        [TestAction.use_vm_backup, 'backup2'], \
        [TestAction.start_vm, "vm1"], \
	[TestAction.create_volume_snapshot, "vm1-root", "snapshot3"], \
        [TestAction.create_volume_snapshot, "vm1-root", "snapshot4"], \
	[TestAction.batch_delete_volume_snapshot, ["snapshot3"]], \
	[TestAction.create_image_from_volume, "vm1", "image1"], \
	[TestAction.create_volume_backup, "volume1", "backup5"], \
	[TestAction.stop_vm, "vm1"], \
        [TestAction.use_vm_backup, 'backup2'],
        [TestAction.start_vm, "vm1"]])
