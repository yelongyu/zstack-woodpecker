import zstackwoodpecker.test_state as ts_header
TestAction = ts_header.TestAction
def path():
    return dict(initial_formation="template2",\
                path_list=[[TestAction.create_data_volume_from_image, "volume1", "=scsi"], \
                [TestAction.attach_volume, "vm1", "volume1"], \
                [TestAction.detach_volume, "volume1"], \
		[TestAction.clone_vm, "vm1", "vm2", "=full"], \
		[TestAction.attach_volume, "vm1", "volume1"], \
		[TestAction.create_volume_backup, "volume1", "backup1"], \
		[TestAction.delete_volume, "volume1"], \
		[TestAction.reboot_vm, "vm1"], \
		[TestAction.create_volume, "volume2", "=scsi"], \
		[TestAction.create_volume_snapshot, "volume2", 'snapshot1'], \
		[TestAction.attach_volume, "vm1", "volume2"], \
		[TestAction.detach_volume, "volume2"], \
		[TestAction.stop_vm, "vm2"], \
		[TestAction.ps_migrate_volume, "vm2-root"], \
		[TestAction.create_volume, "volume3", "=scsi"], \
		[TestAction.start_vm, "vm2"], \
		[TestAction.attach_volume, "vm1", "volume3"], \
		[TestAction.create_volume_backup, "volume3", "backup2"], \
		[TestAction.stop_vm, "vm1"], \
		[TestAction.use_volume_backup, "backup2"], \
		[TestAction.start_vm, "vm1"], \
		[TestAction.reboot_vm, "vm1"]])

