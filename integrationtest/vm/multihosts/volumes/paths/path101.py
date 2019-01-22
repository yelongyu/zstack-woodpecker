import zstackwoodpecker.test_state as ts_header
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template2", path_list=[ \
	[TestAction.create_volume, "volume1"], \
	[TestAction.attach_volume, "vm1", "volume1"], \
	[TestAction.delete_volume, "volume1"], \
	[TestAction.create_volume_snapshot, "vm1-root", "snapshot1"], \
	[TestAction.create_volume, "volume2"], \
	[TestAction.attach_volume, "vm1", "volume2"] , \
	[TestAction.create_volume_snapshot, "volume2", "snapshot2"], \
	[TestAction.stop_vm, "vm1"], \
	[TestAction.use_volume_snapshot, "snapshot2"], \
	[TestAction.start_vm, "vm1"], \
	[TestAction.delete_volume, "volume2"], \
	[TestAction.create_volume, "volume3"], \
	[TestAction.attach_volume, "vm1", "volume3"] , \
	[TestAction.delete_volume, "volume3"], \
	[TestAction.reboot_vm, "vm1"], \
	[TestAction.create_volume, "volume4"], \
	[TestAction.attach_volume, "vm1", "volume4"], \
	[TestAction.detach_volume, "volume4"], \
	[TestAction.stop_vm, "vm1"] , \
	[TestAction.use_volume_snapshot, "snapshot1"], \
	[TestAction.start_vm, "vm1"], \
	[TestAction.attach_volume, "vm1", "volume4"] , \
	[TestAction.create_data_vol_template_from_volume, "volume4", "image1"], \
	[TestAction.reboot_vm, "vm1"]])
