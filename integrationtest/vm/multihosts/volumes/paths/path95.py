import zstackwoodpecker.test_state as ts_header
TestAction = ts_header.TestAction
def path():
    return dict(initial_formation="template2",\
                path_list=[[TestAction.create_volume, "volume1", "=scsi"], \
                [TestAction.attach_volume, "vm1", "volume1"], \
		[TestAction.detach_volume, "volume1"], \
		[TestAction.stop_vm, "vm1"], \
		[TestAction.reinit_vm, "vm1"], \
		[TestAction.create_data_vol_template_from_volume, "volume1", "image1"],\
		[TestAction.delete_volume, "volume1"], \
		[TestAction.create_image_from_volume, "vm1", "image2"], \
		[TestAction.create_volume, "volume2", "=scsi"], \
		[TestAction.start_vm, "vm1"], \
		[TestAction.attach_volume, "vm1", "volume2"], \
		[TestAction.create_volume_backup, "volume2", "backup1"], \
		[TestAction.create_volume_snapshot, "volume2", "snapshot2-1"], \
		[TestAction.create_volume_snapshot, "volume2", "snapshot2-2"], \
		[TestAction.create_volume_snapshot, "volume2", "snapshot2-3"], \
		[TestAction.create_volume_snapshot, "volume2", "snapshot2-4"], \
		[TestAction.detach_volume, "volume2"], \
		[TestAction.delete_volume_snapshot, "snapshot2-4"], \
		[TestAction.attach_volume, "vm1", "volume2"], \
		[TestAction.detach_volume, "volume2"], \
		[TestAction.migrate_vm, "vm1"], \
		[TestAction.migrate_vm, "vm1"], \
		[TestAction.create_data_vol_template_from_volume, "volume2", "image3"],\
		[TestAction.batch_delete_volume_snapshot, ["snapshot2-1","snapshot2-2"]], \
		[TestAction.reboot_vm, "vm1"]])
