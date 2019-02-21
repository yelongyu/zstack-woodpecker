import zstackwoodpecker.test_state as ts_header
TestAction = ts_header.TestAction
def path():
    return dict(initial_formation="template2", 
                path_list=[[TestAction.create_data_volume_from_image, "volume1"],
                [TestAction.attach_volume, "vm1", "volume1"], 
                [TestAction.detach_volume, "volume1"], 
		[TestAction.clone_vm, "vm1", "vm2", "full"], 
		[TestAction.stop_vm, "vm2"], 
		[TestAction.ps_migrate_volume, "vm2-root"], 
		[TestAction.ps_migrate_volume, "volume1"], 
		[TestAction.create_data_volume_from_image, "volume2"], 
		[TestAction.attach_volume, "vm1", "volume2"], 
		[TestAction.create_volume_snapshot, "vm1-root", "snapshot1"], 
		[TestAction.create_data_vol_template_from_volume, "volume2", "image1"],
		[TestAction.delete_volume, "volume2"], 
		[TestAction.stop_vm, "vm1"], 
		[TestAction.change_vm_image, "vm1"], 
		[TestAction.create_data_volume_from_image, "volume3"],
		[TestAction.create_volume_snapshot, "volume3", "snapshot2"], 
		[TestAction.start_vm, "vm1"], 
		[TestAction.reboot_vm, "vm1"]])
