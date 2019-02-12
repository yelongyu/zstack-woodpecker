import zstackwoodpecker.test_state as ts_header
TestAction = ts_header.TestAction
def path():
        return dict(initial_formation="template2",
                path_list=[[TestAction.create_volume, "volume1", "=scsi"], \
		[TestAction.create_volume, "volume2", "=scsi"], \
		[TestAction.create_volume, "volume3", "=scsi"], \
		[TestAction.create_volume, "volume4", "=scsi"], \
		[TestAction.create_volume, "volume5", "=scsi"], \
		[TestAction.create_volume, "volume6", "=scsi"], \
		[TestAction.create_volume, "volume7", "=scsi"], \
		[TestAction.create_volume, "volume8", "=scsi"], \
		[TestAction.attach_volume, "vm1", "volume1"], \
		[TestAction.create_image_from_volume, "vm1", "image1"], \
		[TestAction.create_volume_backup, "volume1", "backup1"], \
		[TestAction.delete_volume, "volume2"], \
		[TestAction.stop_vm, "vm1"], \
		[TestAction.cleanup_ps_cache], \
		[TestAction.use_volume_backup, "backup1"], \
		[TestAction.start_vm, "vm1"], \
		[TestAction.attach_volume, "vm1", "volume3"], \
		[TestAction.create_image_from_volume, "vm1", "image2"], \
		[TestAction.create_volume_backup, "volume3", "backup2"], \
		[TestAction.stop_vm, "vm1"], \
		[TestAction.use_volume_backup, "backup2"], \
		[TestAction.start_vm, "vm1"], \
		[TestAction.reboot_vm, "vm1"]])
