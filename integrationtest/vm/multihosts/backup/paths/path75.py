import zstackwoodpecker.test_state as ts_header
TestAction = ts_header.TestAction
def path():
    return dict(initial_formation="template2", \
		path_list=[[TestAction.create_volume, "volume1","=scsi"], \
		[TestAction.attach_volume, "vm1", "volume1"], \
                [TestAction.create_volume_backup, "volume1", "backup-volume-1","full"], \
                [TestAction.clone_vm, "vm1", "vm2"], \
                [TestAction.stop_vm, "vm1"], \
                [TestAction.use_volume_backup, "backup-volume-1"], \
                [TestAction.create_volume_snapshot, "vm1-root", "snapshot-root1"], \
                [TestAction.use_volume_snapshot, "snapshot-root1"], \
                [TestAction.start_vm, "vm1"], \
                [TestAction.create_data_vol_template_from_volume, "volume1", "image1"], \
                [TestAction.create_vm_backup, "vm1", "backup-vm-1", "full"], \
                [TestAction.stop_vm, "vm1"], \
                [TestAction.use_vm_backup, "backup-vm-1"], \
                [TestAction.use_volume_snapshot, "snapshot-root1"], \
                [TestAction.start_vm, "vm1"], \
                [TestAction.delete_volume, "volume1"], \
                [TestAction.create_volume, "volume2", "=scsi"], \
                [TestAction.attach_volume, "vm1", "volume2"], \
                [TestAction.create_volume_backup, "volume2", "backup-volume2-1", "full"], \
                [TestAction.stop_vm, "vm1"], \
                [TestAction.use_vm_backup, "backup-vm-1"], \
                ])
