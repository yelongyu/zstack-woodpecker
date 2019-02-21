import zstackwoodpecker.test_state as ts_header
TestAction = ts_header.TestAction
def path():
        return dict(initial_formation="template2",
                path_list=[[TestAction.create_volume, "volume1","=scsi"], \
                [TestAction.delete_volume, "volume1"], \
		[TestAction.create_volume, "volume2","=scsi"], \
		[TestAction.delete_volume, "volume2"], \
		[TestAction.create_volume, "volume3","=scsi"], \
		[TestAction.delete_volume, "volume3"], \
		[TestAction.create_volume, "volume4","=scsi"], \
		[TestAction.delete_volume, "volume4"], \
		[TestAction.create_volume, "volume5","=scsi"], \
		[TestAction.delete_volume, "volume5"], \
		[TestAction.create_volume, "volume6","=scsi"], \
		[TestAction.delete_volume, "volume6"], \
		[TestAction.create_volume, "volume7","=scsi"], \
		[TestAction.delete_volume, "volume7"], \
		[TestAction.create_volume, "volume8","=scsi"], \
		[TestAction.delete_volume, "volume8"], \
		[TestAction.migrate_vm, "vm1"], \
		[TestAction.migrate_vm, "vm1"], \
		[TestAction.create_volume, "volume9","=scsi"], \
		[TestAction.attach_volume, "vm1", "volume9"], \
		[TestAction.create_volume_backup, "volume9", "backup1"], \
		[TestAction.detach_volume, "volume9"], \
		[TestAction.create_volume_snapshot, "vm1-root", "snapshot1"], \
		[TestAction.create_data_vol_template_from_volume, "volume9", "image1"],\
		[TestAction.attach_volume, "vm1", "volume9"], \
		[TestAction.detach_volume, "volume9"], \
		[TestAction.stop_vm, "vm1"], \
		[TestAction.reinit_vm, "vm1"], \
		[TestAction.start_vm, "vm1"], \
		[TestAction.attach_volume, "vm1", "volume9"], \
		[TestAction.stop_vm, "vm1"], \
		[TestAction.use_volume_backup, "backup1"], \
		[TestAction.start_vm, "vm1"], \
		[TestAction.reboot_vm, "vm1"]])
