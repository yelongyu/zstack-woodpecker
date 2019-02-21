import zstackwoodpecker.test_state as ts_header
TestAction = ts_header.TestAction
def path():
        return dict(initial_formation="template2",
		path_list=[[TestAction.create_volume, "volume1"], \
		[TestAction.delete_volume, "volume1"], \
		[TestAction.stop_vm, "vm1"], \
		[TestAction.cleanup_ps_cache], \
		[TestAction.create_volume, "volume2"], \
		[TestAction.start_vm, "vm1"], \
		[TestAction.attach_volume, "vm1", "volume2"], \
		[TestAction.create_volume_backup, "volume2", "backup1"], \
		[TestAction.detach_volume, "volume2"], \
		[TestAction.clone_vm, "vm1", "vm2", "=full"], \
		[TestAction.stop_vm, "vm2"], \
		[TestAction.ps_migrate_volume, "vm2-root"], \
		[TestAction.attach_volume, "vm1", "volume2"], \
		[TestAction.stop_vm, "vm1"], \
		[TestAction.use_volume_backup, "backup1"], \
		[TestAction.delete_volume, "volume2"], \
		[TestAction.start_vm, "vm1"], \
		[TestAction.reboot_vm, "vm1"], \
		[TestAction.create_volume, "volume3"], \
		[TestAction.attach_volume, "vm1", "volume3"], \
		[TestAction.create_volume_backup, "volume3", "backup2"], \
		[TestAction.stop_vm, "vm1"], \
		[TestAction.use_volume_backup, "backup2"], \
		[TestAction.start_vm, "vm1"], \
		[TestAction.reboot_vm, "vm1"]])		
