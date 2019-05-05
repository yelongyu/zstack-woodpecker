import zstackwoodpecker.test_state as ts_header
TestAction = ts_header.TestAction
def path():
	return dict(initial_formation="template2", 
		path_list=[[TestAction.create_volume, "volume1", "=scsi"],\
		[TestAction.attach_volume, "vm1", "volume1"], \
		[TestAction.create_volume, "volume2", "=scsi"],\
		[TestAction.attach_volume, "vm1", "volume2"], \
		[TestAction.delete_volume, "volume2"], \
		[TestAction.cleanup_ps_cache], \
		[TestAction.create_volume_snapshot, "volume1", "snapshot4"], \
		[TestAction.create_volume_snapshot, "volume1", "snapshot5"], \
                [TestAction.create_volume_snapshot, "volume1", "snapshot6"], \
		[TestAction.detach_volume, "volume1"], \
		[TestAction.stop_vm, "vm1"], \
		[TestAction.ps_migrate_volume, "vm1-root"], \
		[TestAction.start_vm, "vm1"], \
		[TestAction.ps_migrate_volume, "volume1"], \
		[TestAction.use_volume_snapshot, "snapshot4"], \
		#[TestAction.batch_delete_volume_snapshot, ["snapshot4", "snapshot5"]], \
		[TestAction.attach_volume, "vm1", "volume1"], \
		[TestAction.stop_vm, "vm1"], \
		#[TestAction.reinit_vm, "vm1"], \
		[TestAction.start_vm, "vm1"], \
		[TestAction.resize_data_volume, "volume1", 5*1024*1024], \
		[TestAction.delete_volume_snapshot, "snapshot6"], \
		[TestAction.reboot_vm, "vm1"]])
