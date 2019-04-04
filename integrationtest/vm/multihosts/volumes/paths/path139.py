import zstackwoodpecker.test_state as ts_header
TestAction = ts_header.TestAction
def path():
	return dict(initial_formation="template2", 
		path_list=[[TestAction.create_volume, "volume1", "=scsi"],\
		[TestAction.attach_volume, "vm1", "volume1"], \
		[TestAction.create_volume, "volume2", "=scsi"],\
		[TestAction.cleanup_ps_cache], \
		[TestAction.detach_volume, "volume1"], \
		[TestAction.ps_migrate_volume, "volume1"], \
		[TestAction.create_image_from_volume, "vm1", "image1"], \
		[TestAction.stop_vm, "vm1"], \
                [TestAction.ps_migrate_volume, "vm1-root"], \
		[TestAction.start_vm, "vm1"], \
		[TestAction.attach_volume, "vm1", "volume1"], \
		[TestAction.create_volume_backup, "volume1", "backup1"], \
		[TestAction.create_volume_snapshot, "volume1", "snapshot7"], \
		[TestAction.create_volume_snapshot, "volume1", "snapshot8"], \
                [TestAction.create_volume_snapshot, "volume1", "snapshot9"], \
		[TestAction.batch_delete_volume_snapshot, ["snapshot7", "snapshot8"]], \
		[TestAction.detach_volume, "volume1"], \
		[TestAction.create_image_from_volume, "vm1", "image2"], \
		[TestAction.use_volume_backup, "backup1"], \
		[TestAction.batch_delete_volume_snapshot, ["snapshot9"]], \
		[TestAction.reboot_vm, "vm1"]])

