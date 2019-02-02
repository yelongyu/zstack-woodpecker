import zstackwoodpecker.test_state as ts_header
TestAction = ts_header.TestAction
def path():
    return dict(initial_formation="template2",
                path_list=[[TestAction.create_data_volume_from_image, "volume1", "=scsi,shareable"],
                           [TestAction.create_data_volume_from_image, "volume2", "=scsi,shareable"],
                           [TestAction.create_data_volume_from_image, "volume3", "=scsi,shareable"],
                           [TestAction.create_data_volume_from_image, "volume4", "=scsi,shareable"],
                           [TestAction.create_data_volume_from_image, "volume5", "=scsi,shareable"],
                           [TestAction.create_data_volume_from_image, "volume6", "=scsi,shareable"],
                           [TestAction.create_data_volume_from_image, "volume7", "=scsi,shareable"],
                           [TestAction.create_data_volume_from_image, "volume8", "=scsi,shareable"],
                           [TestAction.attach_volume, "vm1", "volume1"],
                           [TestAction.attach_volume, "vm1", "volume2"],
                           [TestAction.attach_volume, "vm1", "volume3"],
                           [TestAction.attach_volume, "vm1", "volume4"],
                           [TestAction.attach_volume, "vm1", "volume5"],
                           [TestAction.attach_volume, "vm1", "volume6"],
                           [TestAction.attach_volume, "vm1", "volume7"],
                           [TestAction.attach_volume, "vm1", "volume8"],
                           [TestAction.detach_volume, "volume1", "vm1"],
                           [TestAction.clone_vm, "vm1", "vm2"],
                           [TestAction.create_data_vol_template_from_volume, "volume1", "image1"],
                           [TestAction.delete_volume, "volume1"],
                           [TestAction.clone_vm, "vm1", "vm3"],
                           [TestAction.resize_volume, "vm1", 5*1024*1024],
                           [TestAction.detach_volume, "volume2", "vm1"],
                           [TestAction.clone_vm, "vm1", "vm4"],
                           [TestAction.resize_volume, "vm1", 5*1024*1024],
                           [TestAction.reboot_vm, "vm1"]
                          ]
               )
