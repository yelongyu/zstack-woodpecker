import zstackwoodpecker.test_state as ts_header
TestAction = ts_header.TestAction
def path():
    return dict(initial_formation="template2", \
                path_list=[[TestAction.create_volume, "volume1"], 
		[TestAction.delete_volume, "volume1"], 
		[TestAction.create_image_from_volume, "vm1", "image1"], 
		[TestAction.create_volume, "volume2"], 
		[TestAction.create_volume_snapshot, "volume2", 'snapshot1'], 
		[TestAction.attach_volume, "vm1", "volume2"], 
		[TestAction.clone_vm, "vm1", "vm2", "full"], 
		[TestAction.create_volume_backup, "volume2", "backup1"], 
		[TestAction.delete_volume, "volume2"], 
		[TestAction.reboot_vm, "vm1"],  
		[TestAction.create_volume, "volume3"], 
		[TestAction.create_volume_snapshot, "volume3", "snapshot2"], 
		[TestAction.use_volume_snapshot, "snapshot2"], 
		[TestAction.reboot_vm, "vm1"]])
