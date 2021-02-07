import zstackwoodpecker.test_state as ts_header
TestAction = ts_header.TestAction
def path():
    return dict(initial_formation="template2", \
                path_list=[[TestAction.create_data_volume_from_image, "volume1"],\
                [TestAction.delete_volume, "volume1"], \
                [TestAction.stop_vm, "vm1"], \
                [TestAction.cleanup_ps_cache], \
                [TestAction.start_vm, "vm1"], \
                [TestAction.create_volume, "volume2", "=scsi"], \
                [TestAction.attach_volume, "vm1", "volume2"], \
                [TestAction.create_volume_backup, "volume2", "backup1"], \
                [TestAction.delete_volume, "volume2"], \
                [TestAction.stop_vm, "vm1"], \
                [TestAction.cleanup_ps_cache], \
                [TestAction.create_volume, "volume3", "=scsi"], \
                [TestAction.create_volume_snapshot, "volume3", "snapshot1"], \
                [TestAction.delete_volume, "volume3"], \
                [TestAction.cleanup_ps_cache], \
                [TestAction.start_vm, "vm1"], \
                [TestAction.create_volume, "volume4", "=scsi"], \
                [TestAction.attach_volume, "vm1", "volume4"], \
                [TestAction.create_volume_backup, "volume4", "backup2"], \
                [TestAction.stop_vm, "vm1"], \
                [TestAction.use_volume_backup, "backup2"], \
                [TestAction.start_vm, "vm1"], \
                [TestAction.reboot_vm, "vm1"]])

