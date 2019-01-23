import zstackwoodpecker.test_state as ts_header
TestAction = ts_header.TestAction
def path():
    return dict(initial_formation="template1", path_list=[[TestAction.reboot_vm, "vm1"], \
				[TestAction.delete_volume, "vm1-volume1"], \
				[TestAction.delete_volume, "vm1-volume2"], \
				[TestAction.delete_volume, "vm1-volume3"], \
				[TestAction.delete_volume, "vm1-volume4"], \
				[TestAction.delete_volume, "vm1-volume5"], \
				[TestAction.delete_volume, "vm1-volume6"], \
				[TestAction.delete_volume, "vm1-volume7"], \
				[TestAction.delete_volume, "vm1-volume8"], \
				[TestAction.create_volume, "volume1"], \
				[TestAction.attach_volume, "vm1", "volume1"], \
				[TestAction.detach_volume, "volume1"], \
				[TestAction.stop_vm, "vm1"], \
				[TestAction.change_vm_image, "vm1"], \
				[TestAction.create_volume_snapshot, "volume1", "snapshot1"], \
				[TestAction.attach_volume, "vm1", "volume1"], \
				[TestAction.detach_volume, "volume1"], \
				[TestAction.ps_migrate_volume, "vm1-root"], \
				[TestAction.ps_migrate_volume, "vm1-root"], \
				[TestAction.use_volume_snapshot, "snapshot1"], \
				[TestAction.attach_volume, "vm1", "volume1"], \
				[TestAction.detach_volume, "volume1"], \
				[TestAction.create_volume_snapshot, "vm1-root", "snapshot2"],\
				[TestAction.create_volume_snapshot, "volume1", "snapshot3"], \
				[TestAction.use_volume_snapshot, "snapshot3"], \
				[TestAction.start_vm, "vm1"], \
				[TestAction.reboot_vm, "vm1"]])

