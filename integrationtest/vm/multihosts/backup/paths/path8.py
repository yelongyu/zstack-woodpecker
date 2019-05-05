import zstackwoodpecker.test_state as ts_header

TestAction = ts_header.TestAction
def path():
    return dict(initial_formation="template2",
        path_list=[[TestAction.create_volume, "volume1", "=scsi"],\
        [TestAction.attach_volume, "vm1", "volume1"], \
        [TestAction.create_volume_backup, "volume1", "backup1"], \
	[TestAction.stop_vm, "vm1"], \
	[TestAction.change_vm_image, "vm1"], \
	[TestAction.start_vm, "vm1"], \
	[TestAction.stop_vm, "vm1"], \
	[TestAction.use_volume_backup, 'backup1'],
	[TestAction.start_vm, "vm1"], \
	[TestAction.create_volume_snapshot, "vm1-root", "snapshot62"], \
	[TestAction.create_volume_snapshot, "vm1-root", "snapshot63"], \
	[TestAction.stop_vm, "vm1"], \
	[TestAction.use_volume_snapshot, "snapshot62"],
	[TestAction.start_vm, "vm1"], \
	[TestAction.create_volume_snapshot, "volume1", "snapshot1"], \
	[TestAction.create_volume_snapshot, "volume1", "snapshot2"], \
	[TestAction.create_vm_backup, "vm1", "backup2"], \
	[TestAction.stop_vm, "vm1"], \
	[TestAction.use_vm_backup, "backup2"], \
	[TestAction.start_vm, "vm1"], \
	[TestAction.create_volume_snapshot, "volume1", "snapshot3"], \
	[TestAction.create_vm_backup, "vm1", "backup3"], \
	[TestAction.stop_vm, "vm1"], \
        [TestAction.use_vm_backup, "backup3"], \
        [TestAction.start_vm, "vm1"]])