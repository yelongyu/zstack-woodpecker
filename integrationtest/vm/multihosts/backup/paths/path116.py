import zstackwoodpecker.test_state as ts_header
TestAction = ts_header.TestAction
def path():
    return dict(initial_formation="template2", \
		path_list=[[TestAction.create_volume, "volume1","=scsi"], \
		[TestAction.attach_volume, "vm1", "volume1"], \
                [TestAction.create_vm_backup, "vm1", "backup-vm-1","full"], \
                [TestAction.stop_vm, "vm1"], \
                [TestAction.change_vm_image, "vm1"], \
                [TestAction.use_vm_backup, "backup-vm-1"], \
                [TestAction.start_vm, "vm1"], \
                [TestAction.create_image_from_volume, "vm1", "image1"], \
                [TestAction.create_volume_snapshot, "volume1", "snapshot-v1"], \
                [TestAction.delete_volume_snapshot, "snapshot-v1"], \
                [TestAction.create_vm_backup, "vm1", "backup-vm-2"], \
                [TestAction.create_volume_backup, "volume1", "backup-volume-1"], \
                [TestAction.stop_vm, "vm1"], \
                [TestAction.use_volume_backup, "backup-volume-1"], \
                [TestAction.create_image_from_volume, "vm1", "image2"], \
                [TestAction.start_vm, "vm1"], \
                [TestAction.create_volume, "volume3", "=scsi"], \
                [TestAction.attach_volume, "vm1", "volume3"], \
                [TestAction.create_vm_backup, "vm1", "backup-vm-3"], \
                [TestAction.stop_vm, "vm1"], \
                [TestAction.use_vm_backup, "backup-vm-3"], \
                ])
