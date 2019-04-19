import zstackwoodpecker.test_state as ts_header
TestAction = ts_header.TestAction
def path():
    return dict(initial_formation="template2", \
		path_list=[[TestAction.create_volume, "volume1","=scsi"], \
		[TestAction.attach_volume, "vm1", "volume1"], \
	        [TestAction.create_volume, "volume2","=scsi"], \
		[TestAction.attach_volume, "vm1", "volume2"], \
		[TestAction.create_volume, "volume3","=scsi"], \
		[TestAction.attach_volume, "vm1", "volume3"], \
		[TestAction.create_volume, "volume4","=scsi"], \
		[TestAction.attach_volume, "vm1", "volume4"], \
		[TestAction.create_volume, "volume5","=scsi"], \
		[TestAction.attach_volume, "vm1", "volume5"], \
		[TestAction.create_volume, "volume6","=scsi"], \
		[TestAction.attach_volume, "vm1", "volume6"], \
		[TestAction.create_volume, "volume7","=scsi"], \
		[TestAction.attach_volume, "vm1", "volume7"], \
		[TestAction.create_volume, "volume8","=scsi"], \
		[TestAction.attach_volume, "vm1", "volume8"], \
                [TestAction.create_volume_backup, "volume1", "backup-volume-1"], \
                [TestAction.create_vm_backup, "vm1", "backup-vm-1"], \
                [TestAction.create_volume_snapshot, "vm1-root", "snapshot-root1"], \
                [TestAction.create_volume_snapshot, "vm1-root", "snapshot-root2"], \
                [TestAction.create_volume_snapshot, "vm1-root", "snapshot-root3"], \
                [TestAction.batch_delete_volume_snapshot, ["snapshot-root2","snapshot-root3"]], \
                [TestAction.stop_vm, "vm1"], \
                [TestAction.use_vm_backup, "backup-vm-1"], \
                [TestAction.change_vm_image, "vm1"], \
                [TestAction.create_image_from_volume, "vm1", "image1"], \
                [TestAction.start_vm, "vm1"], \
                [TestAction.create_volume_backup, "volume2", "backup-volume-2"], \
                [TestAction.stop_vm, "vm1"], \
                [TestAction.use_vm_backup, "backup-vm-1"], \
                [TestAction.reinit_vm, "vm1"], \
		[TestAction.use_volume_snapshot, 'snapshot-root1'], \
                [TestAction.start_vm, "vm1"], \
                [TestAction.create_volume_backup, "volume3", "backup-volume-3"], \
                [TestAction.stop_vm, "vm1"], \
                [TestAction.use_volume_backup, "backup-volume-3"]])
