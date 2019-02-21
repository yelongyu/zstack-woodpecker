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
		[TestAction.stop_vm, "vm1"], \
                [TestAction.reinit_vm, "vm1"], \
		[TestAction.start_vm, "vm1"], \
		[TestAction.create_volume, "volume9"], \
		[TestAction.create_data_vol_template_from_volume, "volume9", "image1"],\
		[TestAction.attach_volume, "vm1", "volume9"], \
		[TestAction.detach_volume, "volume9"], \
		[TestAction.clone_vm, "vm1", "vm2", "=full"], \
		[TestAction.stop_vm, "vm2"], \
		[TestAction.ps_migrate_volume, "vm2-root"], \
		[TestAction.create_volume, "volume10"], \
		[TestAction.attach_volume, "vm1", "volume10"], \
		[TestAction.create_volume_backup, "volume10", "backup1"], \
		[TestAction.detach_volume, "volume10"], \
		[TestAction.cleanup_ps_cache], \
		[TestAction.attach_volume, "vm1", "volume10"], \
		[TestAction.stop_vm, "vm1"], \
		[TestAction.use_volume_backup, "backup1"], \
		[TestAction.start_vm, "vm1"], \
                [TestAction.reboot_vm, "vm1"]])
