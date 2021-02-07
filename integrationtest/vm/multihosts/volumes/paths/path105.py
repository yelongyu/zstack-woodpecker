import zstackwoodpecker.test_state as ts_header
TestAction = ts_header.TestAction
def path():
    return dict(initial_formation="template1", \
        path_list=[[TestAction.delete_volume, "vm1-volume1"], \
        [TestAction.delete_volume, "vm1-volume2"], \
        [TestAction.delete_volume, "vm1-volume3"], \
        [TestAction.delete_volume, "vm1-volume4"], \
        [TestAction.delete_volume, "vm1-volume5"], \
        [TestAction.delete_volume, "vm1-volume6"], \
        [TestAction.delete_volume, "vm1-volume7"], \
        [TestAction.delete_volume, "vm1-volume8"], \
	[TestAction.clone_vm, "vm1", "vm2", "=full"], \
	[TestAction.create_volume, "volume1", "=scsi,shareable"], \
	[TestAction.create_volume, "volume4", "=scsi"], \
	[TestAction.attach_volume, "vm1", "volume1"], \
	[TestAction.attach_volume, "vm1", "volume4"], \
	[TestAction.create_volume, "volume2", "=scsi"], \
	[TestAction.attach_volume, "vm1", "volume2"], \
	[TestAction.create_volume_backup, "volume2", "backup1"], \
	[TestAction.detach_volume, "volume4"], \
	[TestAction.stop_vm, "vm2"], \
	[TestAction.ps_migrate_volume, "vm2-root"], \
	[TestAction.create_volume, "volume3"], \
	[TestAction.attach_volume, "vm1", "volume3"], \
	[TestAction.resize_data_volume, "volume3", 5*1024*1024], \
	[TestAction.delete_volume, "volume3"], \
	[TestAction.create_volume_snapshot, "vm1-root", 'snapshot1'], \
	[TestAction.stop_vm, "vm1"], \
	[TestAction.use_volume_backup, "backup1"], \
	[TestAction.start_vm, "vm1"], \
	[TestAction.reboot_vm, "vm1"]])	
