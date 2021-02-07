import zstackwoodpecker.test_state as ts_header
TestAction = ts_header.TestAction
def path():
        return dict(initial_formation="template2",\
		path_list=[[TestAction.create_volume, "volume1"], \
                [TestAction.attach_volume, "vm1", "volume1"], \
                [TestAction.create_volume, "volume2"], \
                [TestAction.attach_volume, "vm1", "volume2"], \
                [TestAction.create_volume, "volume3"], \
                [TestAction.attach_volume, "vm1", "volume3"], \
                [TestAction.create_volume, "volume4"], \
                [TestAction.attach_volume, "vm1", "volume4"], \
                [TestAction.create_volume, "volume5"], \
                [TestAction.attach_volume, "vm1", "volume5"], \
                [TestAction.create_volume, "volume6"], \
                [TestAction.attach_volume, "vm1", "volume6"], \
                [TestAction.create_volume, "volume7"], \
                [TestAction.attach_volume, "vm1", "volume7"], \
                [TestAction.create_volume, "volume8"], \
                [TestAction.attach_volume, "vm1", "volume8"], \
		[TestAction.detach_volume, "volume1"], \
                [TestAction.detach_volume, "volume2"], \
                [TestAction.detach_volume, "volume3"], \
                [TestAction.detach_volume, "volume4"], \
                [TestAction.detach_volume, "volume5"], \
                [TestAction.detach_volume, "volume6"], \
                [TestAction.detach_volume, "volume7"], \
                [TestAction.detach_volume, "volume8"], \
		[TestAction.clone_vm, "vm1", "vm2", "=full"], \
		[TestAction.create_volume, "volume9"], \
		[TestAction.attach_volume, "vm1", "volume9"], \
		[TestAction.create_volume_backup, "volume9", "backup1"], \
		[TestAction.create_volume_snapshot, "vm1-root", 'snapshot1'], \
		[TestAction.stop_vm, "vm1"], \
		[TestAction.use_volume_snapshot, "snapshot1"], \
		[TestAction.start_vm, "vm1"], \
		[TestAction.detach_volume, "volume9"], \
		[TestAction.ps_migrate_volume, "volume9"], \
		[TestAction.create_volume, "volume10"], \
		[TestAction.attach_volume, "vm1", "volume10"], \
		[TestAction.create_volume_backup, "volume10", "backup2"], \
		[TestAction.stop_vm, "vm1"], \
		[TestAction.use_volume_backup, "backup2"], \
		[TestAction.start_vm, "vm1"], \
                [TestAction.reboot_vm, "vm1"]])

