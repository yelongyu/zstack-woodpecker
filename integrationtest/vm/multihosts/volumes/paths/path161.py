import zstackwoodpecker.test_state as ts_header
TestAction = ts_header.TestAction
def path():
        return dict(initial_formation="template2",
                path_list=[[TestAction.create_volume, "volume1", "=scsi"], \
                [TestAction.attach_volume, "vm1", "volume1"], \
                [TestAction.detach_volume, "volume1"], \
                [TestAction.stop_vm, "vm1"],\
                [TestAction.ps_migrate_volume, "vm1-root"],\
                [TestAction.ps_migrate_volume, "volume1"],\
                [TestAction.start_vm, "vm1"],\
                [TestAction.attach_volume, "vm1", "volume1"], \
                [TestAction.resize_data_volume, "volume1", 510241024], \
                [TestAction.detach_volume, "volume1"], \
                [TestAction.cleanup_ps_cache], \
                [TestAction.create_data_vol_template_from_volume, "volume1", "image1"], \
                [TestAction.create_volume_snapshot, "volume1", "snapshot1"], \
                [TestAction.create_volume_snapshot, "volume1", "snapshot2"], \
                [TestAction.create_volume_snapshot, "volume1", "snapshot3"], \
		[TestAction.delete_volume_snapshot, "snapshot1"], \
		[TestAction.stop_vm, "vm1"],\
		[TestAction.change_vm_image, "vm1"], \
		[TestAction.start_vm, "vm1"],\
		[TestAction.create_data_vol_template_from_volume, "volume1", "image1"], \
		[TestAction.delete_volume_snapshot, "snapshot2"], \
                [TestAction.reboot_vm, "vm1"]])
