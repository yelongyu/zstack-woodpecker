import zstackwoodpecker.test_state as ts_header
TestAction = ts_header.TestAction
def path():
    return dict(initial_formation="template1",\
                path_list=[[TestAction.delete_volume, "vm1-volume1"], \
		[TestAction.delete_volume, "vm1-volume2"], \
		[TestAction.delete_volume, "vm1-volume3"], \
		[TestAction.delete_volume, "vm1-volume4"], \
		[TestAction.delete_volume, "vm1-volume5"], \
		[TestAction.delete_volume, "vm1-volume6"], \
		[TestAction.delete_volume, "vm1-volume7"], \
		[TestAction.delete_volume, "vm1-volume8"], \
		[TestAction.create_volume_snapshot, "vm1-root", 'snapshot1'], \
		[TestAction.create_volume, "volume1"], \
		[TestAction.attach_volume, "vm1", "volume1"], \
		[TestAction.create_volume_backup, "volume1", "backup1"], \
		[TestAction.delete_volume, "volume1"], \
		[TestAction.stop_vm, "vm1"], \
		[TestAction.change_vm_image, "vm1"], \
		[TestAction.start_vm, "vm1"], \
		[TestAction.create_volume, "volume2"], \
		[TestAction.attach_volume, "vm1", "volume2"], \
		[TestAction.create_volume_backup, "volume2", "backup2"], \
		[TestAction.stop_vm, "vm1"], \
		[TestAction.use_volume_backup, "backup2"], \
		[TestAction.detach_volume, "volume2"], \
		[TestAction.use_volume_snapshot, "snapshot1"], \
		[TestAction.start_vm, "vm1"], \
		[TestAction.attach_volume, "vm1", "volume2"], \
		[TestAction.create_volume_backup, "volume2", "backup3"], \
		[TestAction.stop_vm, "vm1"], \
		[TestAction.use_volume_backup, "backup3"], \
		[TestAction.start_vm, "vm1"], \
		[TestAction.reboot_vm, "vm1"]])

