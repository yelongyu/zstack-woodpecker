import zstackwoodpecker.test_state as ts_header
TestAction = ts_header.TestAction
def path():
        return dict(initial_formation="template2",\
                path_list=[[TestAction.create_volume, "volume1", "=scsi"], \
                [TestAction.attach_volume, "vm1", "volume1"], \
                [TestAction.create_volume, "volume2", "=scsi"], \
                [TestAction.attach_volume, "vm1", "volume2"], \
                [TestAction.create_volume, "volume3", "=scsi"], \
                [TestAction.attach_volume, "vm1", "volume3"], \
                [TestAction.create_volume, "volume4", "=scsi"], \
                [TestAction.attach_volume, "vm1", "volume4"], \
                [TestAction.create_volume, "volume5", "=scsi"], \
                [TestAction.attach_volume, "vm1", "volume5"], \
                [TestAction.create_volume, "volume6", "=scsi"], \
                [TestAction.attach_volume, "vm1", "volume6"], \
                [TestAction.create_volume, "volume7","=scsi"], \
                [TestAction.attach_volume, "vm1", "volume7"], \
                [TestAction.create_volume, "volume8", "=scsi"], \
                [TestAction.attach_volume, "vm1", "volume8"], \
                [TestAction.delete_volume, "volume1"], \
                [TestAction.delete_volume, "volume2"], \
                [TestAction.delete_volume, "volume3"], \
                [TestAction.delete_volume, "volume4"], \
                [TestAction.delete_volume, "volume5"], \
                [TestAction.delete_volume, "volume6"], \
                [TestAction.delete_volume, "volume7"], \
                [TestAction.delete_volume, "volume8"], \
		[TestAction.migrate_vm, "vm1"], \
		[TestAction.migrate_vm, "vm1"], \
		[TestAction.create_volume, "volume9", "=scsi"], \
		[TestAction.attach_volume, "vm1", "volume9"], \
		[TestAction.create_volume_backup, "volume9", "backup1"], \
		[TestAction.delete_volume, "volume9"], \
		[TestAction.create_volume, "volume10", "=scsi"], \
		[TestAction.attach_volume, "vm1", "volume10"], \
		[TestAction.create_volume_snapshot, "volume10", 'snapshot1'], \
		[TestAction.detach_volume, "volume10"], \
		[TestAction.ps_migrate_volume, "volume10"], \
		[TestAction.create_volume_snapshot, "vm1-root", 'snapshot2'], \
		[TestAction.stop_vm, "vm1"], \
		[TestAction.use_volume_snapshot, "snapshot2"], \
		[TestAction.start_vm, "vm1"], \
		[TestAction.create_volume, "volume11", "=scsi"], \
		[TestAction.attach_volume, "vm1", "volume11"], \
		[TestAction.create_volume_backup, "volume11", "backup2"], \
		[TestAction.stop_vm, "vm1"], \
		[TestAction.use_volume_backup, "backup2"], \
		[TestAction.start_vm, "vm1"], \
		[TestAction.reboot_vm, "vm1"]])
