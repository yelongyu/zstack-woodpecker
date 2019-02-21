import zstackwoodpecker.test_state as ts_header
TestAction = ts_header.TestAction
def path():
    return dict(initial_formation="template2",\
                path_list=[[TestAction.create_volume, "volume1", "=scsi,shareable"], \
		[TestAction.attach_volume, "vm1", "volume1"], \
		[TestAction.create_volume, "volume2", "=scsi,shareable"], \
		[TestAction.attach_volume, "vm1", "volume2"], \
		[TestAction.create_volume, "volume3", "=scsi,shareable"], \
		[TestAction.attach_volume, "vm1", "volume3"], \
		[TestAction.create_volume, "volume4", "=scsi,shareable"], \
		[TestAction.attach_volume, "vm1", "volume4"], \
		[TestAction.create_volume, "volume5", "=scsi,shareable"], \
		[TestAction.attach_volume, "vm1", "volume5"], \
		[TestAction.create_volume, "volume6", "=scsi,shareable"], \
		[TestAction.attach_volume, "vm1", "volume6"], \
		[TestAction.create_volume, "volume7", "=scsi,shareable"], \
		[TestAction.attach_volume, "vm1", "volume7"], \
		[TestAction.create_volume, "volume8", "=scsi,shareable"], \
		[TestAction.attach_volume, "vm1", "volume8"], \
		[TestAction.detach_volume, "volume1", "vm1"], \
		[TestAction.detach_volume, "volume2", "vm1"], \
		[TestAction.detach_volume, "volume3", "vm1"], \
		[TestAction.detach_volume, "volume4", "vm1"], \
		[TestAction.detach_volume, "volume5", "vm1"], \
		[TestAction.detach_volume, "volume6", "vm1"], \
		[TestAction.detach_volume, "volume7", "vm1"], \
		[TestAction.detach_volume, "volume8", "vm1"], \
		[TestAction.clone_vm, "vm1", "vm2", "full"], \
		[TestAction.stop_vm, "vm2"], \
		[TestAction.ps_migrate_volume, "vm2-root"], \
		[TestAction.resize_data_volume, "volume1", 5*1024*1024], \
		[TestAction.delete_volume, "volume1"], \
		[TestAction.migrate_vm, "vm1"], \
		[TestAction.migrate_vm, "vm1"], \
		[TestAction.resize_data_volume, "volume2", 5*1024*1024], \
		[TestAction.delete_volume, "volume2"], \
		[TestAction.stop_vm, "vm1"], \
		[TestAction.reinit_vm, "vm1"], \
		[TestAction.create_volume_snapshot, "volume3", 'snapshot1'], \
		[TestAction.start_vm, "vm1"], \
		[TestAction.reboot_vm, "vm1"]])
