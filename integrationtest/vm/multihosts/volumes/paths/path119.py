import zstackwoodpecker.test_state as ts_header
TestAction = ts_header.TestAction
def path():
    return dict(initial_formation="template4",\
                path_list=[[TestAction.delete_volume, "vm1-volume1"], \
		[TestAction.reboot_vm, "vm1"], \
		[TestAction.create_volume, "volume1", "=scsi"], \
		[TestAction.attach_volume, "vm1", "volume1"], \
		[TestAction.create_volume_backup, "volume1", "backup1"], \
		[TestAction.stop_vm, "vm1"], \
		[TestAction.cleanup_ps_cache], \
		[TestAction.start_vm, "vm1"], \
		[TestAction.create_volume_snapshot, "volume1", 'snapshot1'], \
		[TestAction.create_volume_snapshot, "volume1", 'snapshot2'], \
		[TestAction.create_volume_snapshot, "volume1", 'snapshot3'], \
		[TestAction.create_volume_snapshot, "volume1", 'snapshot4'], \
		[TestAction.create_volume_snapshot, "volume1", 'snapshot5'], \
		[TestAction.batch_delete_volume_snapshot, ['snapshot3','snapshot5']], \
		[TestAction.detach_volume, "volume1"], \
		[TestAction.clone_vm, "vm1", "vm2", "=full"], \
		[TestAction.attach_volume, "vm1", "volume1"], \
		[TestAction.stop_vm, "vm1"], \
		[TestAction.use_volume_backup, "backup1"], \
		[TestAction.delete_volume_snapshot, 'snapshot1'], \
		[TestAction.start_vm, "vm1"], \
		[TestAction.reboot_vm, "vm1"]])
