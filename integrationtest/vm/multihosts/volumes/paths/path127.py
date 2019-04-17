import zstackwoodpecker.test_state as ts_header
TestAction = ts_header.TestAction
def path():
    return dict(initial_formation="template2",
                path_list=[[TestAction.create_volume, "volume1", "=scsi"], \
                [TestAction.attach_volume, "vm1", "volume1"], \
                [TestAction.create_volume, "volume2", "=scsi"], \
                [TestAction.attach_volume, "vm1", "volume2"], \
                [TestAction.create_volume, "volume3", "=scsi"], \
                [TestAction.attach_volume, "vm1", "volume3"], \
                [TestAction.create_volume, "volume4", "=scsi"], \
                [TestAction.attach_volume, "vm1", "volume4"], \
                [TestAction.create_volume, "volume5", "=scsi"], \
                [TestAction.attach_volume, "vm1", "volume5"], \
                [TestAction.create_volume, "volume6", "=scsi"], \
                [TestAction.attach_volume, "vm1", "volume6"], \
                [TestAction.create_volume, "volume7", "=scsi"], \
                [TestAction.attach_volume, "vm1", "volume7"], \
                [TestAction.create_volume, "volume8", "=scsi"], \
                [TestAction.attach_volume, "vm1", "volume8"], \
                [TestAction.detach_volume, "volume1"], \
                [TestAction.detach_volume, "volume2"], \
                [TestAction.detach_volume, "volume3"], \
                [TestAction.detach_volume, "volume4"], \
                [TestAction.detach_volume, "volume5"], \
                [TestAction.detach_volume, "volume6"], \
                [TestAction.detach_volume, "volume7"], \
                [TestAction.detach_volume, "volume8"], \
		[TestAction.stop_vm, "vm1"], \
		[TestAction.change_vm_image, "vm1"], \
		[TestAction.start_vm, "vm1"], \
		[TestAction.create_volume, "volume1", "=scsi"], \
		[TestAction.resize_data_volume, "volume1", 5*1024*1024], \
		[TestAction.attach_volume, "vm1", "volume1"], \
		[TestAction.create_data_vol_template_from_volume, "volume1", "image1"], \
                [TestAction.create_volume_snapshot, "volume1", "snapshot1"], \
                [TestAction.delete_volume_snapshot, "snapshot1"], \
		[TestAction.delete_volume, "volume1"], \
		[TestAction.cleanup_ps_cache], \
		[TestAction.create_volume, "volume1", "=scsi"], \
		[TestAction.resize_data_volume, "volume1", 5*1024*1024], \
                [TestAction.create_volume_snapshot, "volume1", "snapshot1"], \
                [TestAction.create_volume_snapshot, "volume1", "snapshot2"], \
                [TestAction.create_volume_snapshot, "volume1", "snapshot3"], \
                [TestAction.create_volume_snapshot, "volume1", "snapshot4"], \
                [TestAction.create_volume_snapshot, "volume1", "snapshot5"], \
                [TestAction.batch_delete_volume_snapshot, ["snapshot2", "snapshot3", "snapshot5"]], \
		[TestAction.reboot_vm, "vm1"]])
