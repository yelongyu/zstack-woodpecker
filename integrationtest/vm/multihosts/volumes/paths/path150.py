import zstackwoodpecker.test_state as ts_header
TestAction = ts_header.TestAction
def path():
	return dict(initial_formation="template2", 
		path_list=[[TestAction.create_volume, "volume1", "=scsi"], \
		[TestAction.attach_volume, "vm1", "volume1"], \
		[TestAction.detach_volume, "volume1"], \
		[TestAction.migrate_vm, "vm1"], \
		[TestAction.create_data_vol_template_from_volume, "volume1", "image1"], \
		[TestAction.stop_vm, "vm1"], \
		[TestAction.reinit_vm, "vm1"],\
		[TestAction.start_vm, "vm1"], \
		[TestAction.create_volume_snapshot, "volume1", "snapshot51"], \
		[TestAction.create_volume_snapshot, "volume1", "snapshot52"], \
		[TestAction.create_volume_snapshot, "volume1", "snapshot53"], \
		[TestAction.batch_delete_volume_snapshot, ["snapshot52", "snapshot51"]], \
		[TestAction.ps_migrate_volume, "vm1-root"],\
		[TestAction.resize_data_volume, "volume1", 5*1024*1024], \
		[TestAction.delete_volume_snapshot, "snapshot3"], \
                [TestAction.reboot_vm, "vm1"]])
