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
		[TestAction.create_volume, "volume9","=scsi"], \
		[TestAction.attach_volume, "vm1", "volume9"], \
		[TestAction.create_volume_snapshot, "vm1-root", 'snapshot1'], \
		[TestAction.create_volume_backup, "volume9", "backup1"], \
		[TestAction.detach_volume, "volume9"], \
		[TestAction.stop_vm, "vm1"], \
		[TestAction.reinit_vm, "vm1"], \
		[TestAction.ps_migrate_volume, "volume9"], \
		[TestAction.delete_volume, "volume9"], \
		[TestAction.create_volume_snapshot, "vm1-root", 'snapshot2'], \
		[TestAction.stop_vm, "vm1"], \
		[TestAction.use_volume_snapshot, "snapshot2"], \
		[TestAction.start_vm, "vm1"], \
		[TestAction.create_volume, "volume10","=scsi"], \
		[TestAction.attach_volume, "vm1", "volume10"], \
		[TestAction.create_volume_backup, "volume10", "backup2"], \
		[TestAction.stop_vm, "vm1"], \
		[TestAction.use_volume_backup, "backup2"], \
		[TestAction.start_vm, "vm1"], \
		[TestAction.reboot_vm, "vm1"]])

