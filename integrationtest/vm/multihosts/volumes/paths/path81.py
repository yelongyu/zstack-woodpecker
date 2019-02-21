import zstackwoodpecker.test_state as ts_header
TestAction = ts_header.TestAction
def path():
    return dict(initial_formation="template3",
                path_list=[[TestAction.delete_volume, "vm1-volume1"],
                [TestAction.create_volume, "volume1"],
                [TestAction.attach_volume, "vm1", "volume1"],
                [TestAction.detach_volume, "volume1"],
                [TestAction.stop_vm, "vm1"],
		[TestAction.reinit_vm, "vm1"],
		[TestAction.create_volume_snapshot, "volume1", 'snapshot1'],
		[TestAction.delete_volume, "volume1"],
		[TestAction.change_vm_image, "vm1"],
		[TestAction.create_volume, "volume2"],
		[TestAction.create_volume_snapshot, "volume2", 'snapshot2'],
		[TestAction.start_vm, "vm1"],
		[TestAction.attach_volume, "vm1", "volume2"],
		[TestAction.detach_volume, "volume2"],
		[TestAction.stop_vm, "vm1"],
		[TestAction.reinit_vm, "vm1"],
		[TestAction.ps_migrate_volume, "volume2"],
		[TestAction.start_vm, "vm1"],
		[TestAction.reboot_vm, "vm1"]])

