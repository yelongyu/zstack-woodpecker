import zstackwoodpecker.test_state as ts_header
TestAction = ts_header.TestAction
def path():
    return dict(initial_formation="template2", \
		path_list=[[TestAction.create_volume, "volume1","=scsi"], \
		[TestAction.attach_volume, "vm1", "volume1"], \
                [TestAction.stop_vm, "vm1"], \
                [TestAction.change_vm_image, "vm1"], \
                [TestAction.start_vm, "vm1"], \
                [TestAction.create_volume_backup, "volume1", "backup-volume-1"], \
                [TestAction.stop_vm, "vm1"], \
                [TestAction.use_volume_backup, "backup-volume-1"], \
                [TestAction.create_volume_snapshot, "vm1-root", "snapshot-root1"], \
                [TestAction.create_volume_snapshot, "vm1-root", "snapshot-root2"], \
                [TestAction.create_volume_snapshot, "vm1-root", "snapshot-root3"], \
                [TestAction.create_volume_snapshot, "vm1-root", "snapshot-root4"], \
                [TestAction.create_volume_snapshot, "volume1", "snapshot-volume1-1"], \
                [TestAction.batch_delete_volume_snapshot, ["snapshot-root4","snapshot-root3"]], \
                [TestAction.use_volume_snapshot, "snapshot-volume1-1"], \
                [TestAction.start_vm, "vm1"], \
                [TestAction.create_volume_backup, "volume1", "backup-volume-2"], \
                [TestAction.stop_vm, "vm1"], \
                [TestAction.use_volume_backup, "backup-volume-2"], \
                [TestAction.batch_delete_volume_snapshot, ["snapshot-root1","snapshot-root2"]], \
                [TestAction.detach_volume, "volume1"], \
                [TestAction.start_vm, "vm1"], \
                [TestAction.attach_volume, "vm1", "volume1"], \
                [TestAction.create_volume_backup, "volume1", "backup-volume-3"], \
                [TestAction.stop_vm, "vm1"], \
                [TestAction.use_volume_backup, "backup-volume-3"]])
