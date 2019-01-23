import zstackwoodpecker.test_state as ts_header
TestAction = ts_header.TestAction
def path():
    return dict(initial_formation="template2", \
		path_list=[[TestAction.create_data_volume_from_image, "volume1", "=scsi"],\
		[TestAction.create_data_volume_from_image, "volume2", "=scsi"], \
		[TestAction.create_data_volume_from_image, "volume3", "=scsi"], \
		[TestAction.create_data_volume_from_image, "volume4", "=scsi"], \
		[TestAction.create_data_volume_from_image, "volume5", "=scsi"], \
		[TestAction.create_data_volume_from_image, "volume6", "=scsi"], \
		[TestAction.create_data_volume_from_image, "volume7", "=scsi"], \
		[TestAction.create_data_volume_from_image, "volume8", "=scsi"], \
		[TestAction.delete_volume, "volume1"], \
		[TestAction.delete_volume, "volume2"], \
		[TestAction.delete_volume, "volume3"], \
		[TestAction.delete_volume, "volume4"], \
		[TestAction.delete_volume, "volume5"], \
		[TestAction.delete_volume, "volume6"], \
		[TestAction.delete_volume, "volume7"], \
		[TestAction.delete_volume, "volume8"], \
		[TestAction.cleanup_ps_cache], \
		[TestAction.create_volume, "volume1","=scsi"], \
		[TestAction.create_volume_snapshot, "volume1", 'snapshot1'], \
		[TestAction.attach_volume, "vm1", "volume1"], \
		[TestAction.detach_volume, "volume1"], \
		[TestAction.stop_vm, "vm1"], \
		[TestAction.reinit_vm, "vm1"], \
		[TestAction.start_vm, "vm1"], \
		[TestAction.attach_volume, "vm1", "volume1"], \
		[TestAction.create_volume_backup, "volume1", "backup1"], \
		[TestAction.detach_volume, "volume1"], \
		[TestAction.stop_vm, "vm1"], \
		[TestAction.ps_migrate_volume, "vm1-root"], \
		[TestAction.use_volume_snapshot, "snapshot1"], \
		[TestAction.start_vm, "vm1"], \
		[TestAction.reboot_vm, "vm1"]])

