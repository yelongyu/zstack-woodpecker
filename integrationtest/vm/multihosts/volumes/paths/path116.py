import zstackwoodpecker.test_state as ts_header
TestAction = ts_header.TestAction
def path():
    return dict(initial_formation="template2",\
                path_list=[[TestAction.create_volume, "volume1", "=scsi"], \
		[TestAction.attach_volume, "vm1", "volume1"], \
		[TestAction.reboot_vm, "vm1"], \
		[TestAction.create_volume_backup, "volume1", "backup1"], \
		[TestAction.create_volume, "volume2", "=scsi"], \
		[TestAction.attach_volume, "vm1", "volume2"], \
		[TestAction.reboot_vm, "vm1"], \
		[TestAction.create_data_vol_template_from_volume, "volume2", "image1"],\
		[TestAction.delete_volume, "volume1"], \
		[TestAction.detach_volume, "volume2"], \
		[TestAction.stop_vm, "vm1"], \
		[TestAction.change_vm_image, "vm1"], \
		[TestAction.start_vm, "vm1"], \
		[TestAction.create_volume, "volume3", "=scsi"], \
		[TestAction.create_volume, "volume4", "=scsi,shareable"], \
		[TestAction.attach_volume, "vm1", "volume3"], \
		[TestAction.create_volume_backup, "volume3", "backup2"], \
		[TestAction.stop_vm, "vm1"], \
		[TestAction.use_volume_backup, "backup2"], \
		[TestAction.start_vm, "vm1"], \
		[TestAction.reboot_vm, "vm1"]])