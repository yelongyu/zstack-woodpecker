import zstackwoodpecker.test_state as ts_header
TestAction = ts_header.TestAction
def path():
	return dict(initial_formation="template2", 
		path_list=[[TestAction.create_volume, "volume1", "=scsi"],\
		[TestAction.attach_volume, "vm1", "volume1"], \
		[TestAction.create_volume, "volume2", "=scsi"],\
		[TestAction.delete_volume, "volume2"], \
		[TestAction.create_volume_snapshot, "vm1-root", "snapshot61"],
		[TestAction.resize_data_volume, "volume1", 5*1024*1024], \
		[TestAction.stop_vm, "vm1"], \
		[TestAction.use_volume_snapshot, "snapshot61"], \
		[TestAction.start_vm, "vm1"], \
		[TestAction.create_volume_snapshot, "volume1", "snapshot62"], \
		[TestAction.create_volume_snapshot, "volume1", "snapshot63"], \
		[TestAction.batch_delete_volume_snapshot, ["snapshot63"]],
		[TestAction.clone_vm, "vm1", "vm2"], \
		[TestAction.create_volume_snapshot, "volume1", "snapshot64"], \
		[TestAction.batch_delete_volume_snapshot, ["snapshot64"]],
		[TestAction.reboot_vm, "vm1"]])
				
		
