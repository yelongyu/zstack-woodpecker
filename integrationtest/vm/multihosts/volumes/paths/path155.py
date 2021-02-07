import zstackwoodpecker.test_state as ts_header
TestAction = ts_header.TestAction
def path():
	return dict(initial_formation="template2", 
		path_list=[[TestAction.create_volume, "volume1", "=scsi"], \
		[TestAction.attach_volume, "vm1", "volume1"], \
		[TestAction.detach_volume, "volume1"], \
		[TestAction.reboot_vm, "vm1"],\
		[TestAction.create_volume_snapshot, "volume1", "snapshot1"], \
		[TestAction.create_volume_snapshot, "volume1", "snapshot2"], \
		[TestAction.create_volume_snapshot, "volume1", "snapshot3"], \
		[TestAction.attach_volume, "vm1", "volume1"], \
		[TestAction.create_volume_snapshot, "vm1-root", 'vm_snapshot1'], \
		[TestAction.stop_vm, "vm1"],\
		[TestAction.use_volume_snapshot, "snapshot1"], \
		[TestAction.start_vm, "vm1"],\
		[TestAction.batch_delete_volume_snapshot, ["snapshot2", "snapshot1"]], \
		[TestAction.detach_volume, "volume1"], \
		[TestAction.clone_vm, "vm1", "vm2", "=full"], \
		[TestAction.ps_migrate_volume, "volume1"],\
		[TestAction.delete_volume_snapshot, "snapshot3"], \
		[TestAction.reboot_vm, "vm1"]])
