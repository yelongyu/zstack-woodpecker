import zstackwoodpecker.test_state as ts_header
TestAction = ts_header.TestAction
def path():
    return dict(initial_formation="template5", \
        path_list=[[TestAction.delete_volume, "vm1-volume1"], \
        [TestAction.delete_volume, "vm1-volume2"], \
        [TestAction.delete_volume, "vm1-volume3"], \
        [TestAction.delete_volume, "vm1-volume4"], \
        [TestAction.delete_volume, "vm1-volume5"], \
        [TestAction.delete_volume, "vm1-volume6"], \
        [TestAction.delete_volume, "vm1-volume7"], \
        [TestAction.delete_volume, "vm1-volume8"], \
	[TestAction.create_volume, "volume1", "=scsi"], \
	[TestAction.attach_volume, "vm1", "volume1"], \
	[TestAction.detach_volume, "volume1"], \
	[TestAction.clone_vm, "vm1", "vm2", "=full"], \
	[TestAction.stop_vm, "vm2"], \
        [TestAction.ps_migrate_volume, "vm2-root"], \
	[TestAction.attach_volume, "vm1", "volume1"], \
	[TestAction.create_volume_backup, "volume1", "backup1"], \
	[TestAction.create_volume, "volume2"], \
	[TestAction.attach_volume, "vm1", "volume2"], \
	[TestAction.detach_volume, "volume2"], \
	[TestAction.detach_volume, "volume1"], \
	[TestAction.stop_vm, "vm1"], \
	[TestAction.reinit_vm, "vm1"], \
	[TestAction.ps_migrate_volume, "volume2"], \
	[TestAction.delete_volume, "volume2"], \
	[TestAction.start_vm, "vm1"], \
	[TestAction.clone_vm, "vm1", "vm3", "=full"], \
	[TestAction.attach_volume, "vm1", "volume1"], \
	[TestAction.stop_vm, "vm1"], \
	[TestAction.use_volume_backup, "backup1"], \
	[TestAction.start_vm, "vm1"], \
	[TestAction.reboot_vm, "vm1"]])
