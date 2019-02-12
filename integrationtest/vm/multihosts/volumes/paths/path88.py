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
		[TestAction.create_volume, "volume1", "=scsi,shareable"], \
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
		[TestAction.create_volume, "volume9", "=scsi"], \
		[TestAction.create_volume, "volume10", "=scsi"], \
		[TestAction.create_image_from_volume, "vm1", "image1"], \
		[TestAction.attach_volume, "vm1", "volume9"], \
		[TestAction.create_volume_backup, "volume9", "backup1"], \
		[TestAction.delete_volume, "volume9"], \
		[TestAction.reboot_vm, "vm1"], \
		[TestAction.attach_volume, "vm1", "volume10"], \
		[TestAction.create_volume_backup, "volume10", "backup2"], \
		[TestAction.reboot_vm, "vm1"], \
		[TestAction.ps_migrate_volume, "volume3"], \
		[TestAction.reboot_vm, "vm1"]])
