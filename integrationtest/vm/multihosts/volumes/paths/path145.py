import zstackwoodpecker.test_state as ts_header
TestAction = ts_header.TestAction
def path():
	return dict(initial_formation="template2", 
		path_list=[[TestAction.create_volume, "volume1", "=scsi"],\
		[TestAction.create_volume, "volume2", "=scsi"],\
		[TestAction.attach_volume, "vm1", "volume1"], \
		[TestAction.detach_volume, "volume1"], \
		[TestAction.clone_vm, "vm1", "vm2", "full"], \
		[TestAction.attach_volume, "vm1", "volume1"], \
		[TestAction.create_volume_backup, "volume1", "backup1"], \
		[TestAction.detach_volume, "volume1"], \
		[TestAction.attach_volume, "vm1", "volume1"], \
		[TestAction.create_image_from_volume, "vm1", "image1"], \
		[TestAction.stop_vm, "vm1"], \
		[TestAction.use_volume_backup, "backup1"],
		[TestAction.start_vm, "vm1"], \
		[TestAction.create_volume_snapshot, "volume1", "snapshot41"], \
                [TestAction.create_volume_snapshot, "volume1", "snapshot42"], \
                [TestAction.create_volume_snapshot, "volume1", "snapshot43"], \
		[TestAction.delete_volume_snapshot, "snapshot41"], 
		[TestAction.delete_volume, "volume2"], 
		[TestAction.create_volume_backup, "vm1-root", "backup2"], \
		[TestAction.detach_volume, "volume1"], \
		[TestAction.ps_migrate_volume, "volume1"], \
		[TestAction.delete_volume_snapshot, "snapshot42"],
		[TestAction.reboot_vm, "vm1"]])					
			

	
