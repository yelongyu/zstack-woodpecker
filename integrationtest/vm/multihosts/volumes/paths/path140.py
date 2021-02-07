import zstackwoodpecker.test_state as ts_header
TestAction = ts_header.TestAction
def path():
	return dict(initial_formation="template2", 
		path_list=[[TestAction.create_volume, "volume1", "=scsi"],\
		[TestAction.attach_volume, "vm1", "volume1"], \
		[TestAction.reboot_vm, "vm1"], \
		[TestAction.create_data_vol_template_from_volume, "volume1", "disk_image"], \
		[TestAction.delete_volume, "volume1"],  	
		[TestAction.stop_vm, "vm1"],\
		[TestAction.reinit_vm, "vm1"], \
		[TestAction.create_volume, "volume2", "=scsi"],\
		[TestAction.ps_migrate_volume, "volume2"], \
		[TestAction.create_volume_snapshot, "volume2", "snapshot7"], \
		[TestAction.create_volume_snapshot, "volume2", "snapshot8"], \
                [TestAction.create_volume_snapshot, "volume2", "snapshot9"], \
		[TestAction.delete_volume_snapshot, "snapshot7"], \
		[TestAction.attach_volume, "vm1", "volume2"], \
		[TestAction.create_image_from_volume, "vm1", "image2"], \
		[TestAction.create_volume_backup, "volume2", "backup1"], \
		[TestAction.batch_delete_volume_snapshot, [["snapshot8"], ["snapshot9"]]], \
		[TestAction.start_vm, "vm1"],\
		[TestAction.reboot_vm, "vm1"]])

