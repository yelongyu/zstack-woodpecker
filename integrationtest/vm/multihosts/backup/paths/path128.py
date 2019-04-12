import zstackwoodpecker.test_state as ts_header

TestAction = ts_header.TestAction
def path():
    return dict(initial_formation="template2",
        path_list=[[TestAction.create_volume, "volume1", "=scsi"],\
        [TestAction.attach_volume, "vm1", "volume1"], \
        [TestAction.create_volume_backup, "volume1", "backup1"], \
       	[TestAction.clone_vm, "vm1", "vm2", "=full"], \
        [TestAction.stop_vm, "vm1"], \
        [TestAction.use_volume_backup, 'backup1'],
        [TestAction.start_vm, "vm1"], \
        [TestAction.stop_vm, "vm1"], \
        [TestAction.detach_volume, "volume1"], \
        [TestAction.ps_migrate_volume, "vm1-root"], \
        [TestAction.ps_migrate_volume, "volume1"], \
        [TestAction.attach_volume, "vm1", "volume1"], \
        [TestAction.start_vm, "vm1"], \
        [TestAction.create_volume_snapshot, "volume1", "snapshot62"], \
        [TestAction.create_volume_snapshot, "volume1", "snapshot63"], \
        [TestAction.create_volume_backup, "volume1", "backup2"], \
        [TestAction.use_volume_backup, 'backup2'],
        [TestAction.stop_vm, "vm1"], \
        [TestAction.reinit_vm, "vm1"], \
        [TestAction.start_vm, "vm1"], \
        [TestAction.delete_volume_snapshot, "snapshot62"], \
        [TestAction.create_vm_backup, "vm1", "backup3"], \
        [TestAction.stop_vm, "vm1"], \
        [TestAction.use_vm_backup, "backup3"],
        [TestAction.start_vm, "vm1"]])
