import zstackwoodpecker.test_state as ts_header
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template2", path_list=[
        [TestAction.create_volume, "volume1", "=scsi"],
        [TestAction.create_volume, "volume2", "=scsi"],
        [TestAction.attach_volume,"vm1", "volume1"],
        [TestAction.clone_vm, "vm1", "vm2"],
        [TestAction.attach_volume,"vm2", "volume2"],
	[TestAction.create_data_volume_from_image, "volume3", "=scsi"],
	[TestAction.detach_volume, "volume1"] ,
	[TestAction.stop_vm, "vm1"],
	[TestAction.ps_migrate_volume, "vm1-root"],
	[TestAction.start_vm, "vm1"],
	[TestAction.ps_migrate_volume, "volume1"],
	[TestAction.cleanup_ps_cache],
	[TestAction.resize_data_volume, "volume1", 5*1024*1024],
	[TestAction.detach_volume, "volume2"] ,
	[TestAction.stop_vm, "vm2"],
	[TestAction.ps_migrate_volume, "vm2-root"],
	[TestAction.start_vm, "vm2"],
	[TestAction.ps_migrate_volume, "volume2"],

	[TestAction.reboot_vm, "vm1"]])
