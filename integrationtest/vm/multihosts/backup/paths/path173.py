import zstackwoodpecker.test_state as ts_header

TestAction = ts_header.TestAction
def path():
    return dict(initial_formation="template2",
        path_list=[[TestAction.create_volume, "volume1", "=scsi"],\
        [TestAction.attach_volume, "vm1", "volume1"], \
        [TestAction.create_volume_backup, "volume1", "backup1"], \
	[TestAction.cleanup_ps_cache], \
        [TestAction.stop_vm, "vm1"], \
        [TestAction.use_volume_backup, 'backup1'],
        [TestAction.start_vm, "vm1"], \
        [TestAction.reboot_vm, "vm1"], \
	[TestAction.create_volume_snapshot, "volume1", "snapshot62"], \
        [TestAction.create_volume_snapshot, "volume1", "snapshot63"], \
	[TestAction.stop_vm, "vm1"], \
        [TestAction.use_volume_snapshot, 'snapshot62'],
	[TestAction.start_vm, "vm1"], \
	[TestAction.create_volume_backup, "volume1", "backup2"], \
	[TestAction.stop_vm, "vm1"], \
	[TestAction.change_vm_image, "vm1"], \
	[TestAction.start_vm, "vm1"], \
	[TestAction.resize_data_volume, "volume1", 5*1024*1024], \
	[TestAction.create_volume_backup, "volume1", "backup3"], \
	[TestAction.stop_vm, "vm1"], \
	[TestAction.use_volume_backup, "backup3"],  
	[TestAction.start_vm, "vm1"]])
