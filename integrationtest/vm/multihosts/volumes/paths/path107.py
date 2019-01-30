import zstackwoodpecker.test_state as ts_header
TestAction = ts_header.TestAction
def path():
    return dict(initial_formation="template1", \
        path_list=[[TestAction.delete_volume, "vm1-volume1"], \
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
        [TestAction.reboot_vm, "vm1"], \
        [TestAction.create_data_vol_template_from_volume, "volume1", "image1"],\
        [TestAction.attach_volume, "vm1", "volume1"], \
        [TestAction.detach_volume, "volume1"], \
        [TestAction.migrate_vm, "vm1"], \
        [TestAction.migrate_vm, "vm1"], \
        [TestAction.resize_data_volume, "volume1", 5*1024*1024], \
        [TestAction.attach_volume, "vm1", "volume1"], \
        [TestAction.detach_volume, "volume1"], \
        [TestAction.migrate_vm, "vm1"], \
        [TestAction.migrate_vm, "vm1"], \
        [TestAction.create_volume_snapshot, "volume1", 'snapshot1'], \
        [TestAction.reboot_vm, "vm1"]])

