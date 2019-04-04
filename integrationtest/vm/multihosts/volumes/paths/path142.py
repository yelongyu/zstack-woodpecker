import zstackwoodpecker.test_state as ts_header
TestAction = ts_header.TestAction
def path():
	return dict(initial_formation="template2", 
		path_list=[[TestAction.create_data_volume_from_image, "volume1", "=scsi"],\
		[TestAction.create_data_volume_from_image, "volume2", "=scsi"],\
		[TestAction.delete_volume, "volume2"], \
		[TestAction.stop_vm, "vm1"],\
		[TestAction.change_vm_image, "vm1"], \
		[TestAction.start_vm, "vm1"],\
		[TestAction.attach_volume, "vm1", "volume1"], \
		[TestAction.create_volume_backup, "volume1", "backup1"], \
		[TestAction.detach_volume, "volume1"], \
		[TestAction.attach_volume, "vm1", "volume1"], \
		[TestAction.cleanup_ps_cache], \
		[TestAction.create_volume_backup, "volume1", "backup2"], \
		[TestAction.create_volume_snapshot, "volume1", "snapshot11"], \
                [TestAction.create_volume_snapshot, "volume1", "snapshot21"], \
                [TestAction.create_volume_snapshot, "volume1", "snapshot31"], \
		[TestAction.batch_delete_volume_snapshot, ["snapshot11", "snapshot21"]],\
		[TestAction.stop_vm, "vm1"],\
		[TestAction.change_vm_image, "vm1"], \
		[TestAction.start_vm, "vm1"],\
		[TestAction.create_data_vol_template_from_volume, "volume1", "image2"], \
		[TestAction.delete_volume_snapshot, "snapshot31"], \
		[TestAction.reboot_vm, "vm1"]])
