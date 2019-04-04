import zstackwoodpecker.test_state as ts_header
TestAction = ts_header.TestAction
def path():
	return dict(initial_formation="template2", 
		path_list=[[TestAction.create_data_volume_from_image, "volume1", "=scsi"], \
		[TestAction.attach_volume, "vm1", "volume1"], \
		[TestAction.detach_volume, "volume1"], \
		[TestAction.create_volume_snapshot, "vm1-root", "snapshot1"], \
                [TestAction.create_volume_snapshot, "vm1-root", "snapshot2"], \
                [TestAction.create_volume_snapshot, "vm1-root", "snapshot3"], \
		[TestAction.resize_data_volume, "volume1", 5*1024*1024], \
		[TestAction.stop_vm, "vm1"],\
		[TestAction.use_volume_snapshot, "snapshot1"], \
		[TestAction.start, "vm1"],\
		[TestAction.resize_data_volume, "volume1", 5*1024*1024], \
		[TestAction.create_volume_snapshot, "volume1", "snapshot11"], \
		[TestAction.create_volume_snapshot, "volume1", "snapshot21"], \
		[TestAction.create_volume_snapshot, "volume1", "snapshot31"], \
		[TestAction.batch_delete_volume_snapshot, ["snapshot11","snapshot21"]], \
		[TestAction.attach_volume, "vm1", "volume1"], \
		[TestAction.stop_vm, "vm1"],\
                [TestAction.use_volume_snapshot, "snapshot1"], \
                [TestAction.start, "vm1"],\
		[TestAction.create_data_vol_template_from_volume, "volume1", "image1"], \
		[TestAction.delete_volume_snapshot, "snapshot31"], \
		[TestAction.reboot_vm, "vm1"]])
