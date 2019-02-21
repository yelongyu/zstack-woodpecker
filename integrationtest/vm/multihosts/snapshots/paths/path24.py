import zstackwoodpecker.test_state as ts_header
TestAction = ts_header.TestAction
def path():
    return dict(initial_formation="template1", \
           path_list=[[TestAction.change_global_config_sp_depth, "3"], \
                      [TestAction.create_volume_snapshot, "vm1-root", "snapshot1_1"], \
                      [TestAction.stop_vm, "vm1"], \
                      [TestAction.start_vm, "vm1"], \
                      [TestAction.create_volume_snapshot, "vm1-root", "snapshot2_1"], \
                      [TestAction.stop_vm, "vm1"], \
                      [TestAction.start_vm, "vm1"], \
                      [TestAction.create_volume_snapshot, "vm1-root", "snapshot3_1"], \
                      [TestAction.stop_vm, "vm1"], \
                      [TestAction.use_volume_snapshot, "snapshot2_1"], \
                      [TestAction.start_vm, "vm1"], \
                      [TestAction.create_volume_snapshot, "vm1-root", "snapshot3_2"], \
                      [TestAction.stop_vm, "vm1"], \
                      [TestAction.start_vm, "vm1"], \
                      [TestAction.create_volume_snapshot, "vm1-root", "snapshot4_2"], \
                      [TestAction.stop_vm, "vm1"], \
                      [TestAction.reinit_vm, "vm1"], \
                      [TestAction.start_vm, "vm1"], \
                      [TestAction.create_volume_snapshot, "vm1-root", "snapshot1_3"], \
                      [TestAction.stop_vm, "vm1"], \
                      [TestAction.start_vm, "vm1"], \
                      [TestAction.create_volume_snapshot, "vm1-root", "snapshot2_3"], \
                      [TestAction.stop_vm, "vm1"], \
                      [TestAction.start_vm, "vm1"], \
                      [TestAction.create_volume_snapshot, "vm1-root", "snapshot3_3"], \
                      [TestAction.stop_vm, "vm1"], \
                      [TestAction.use_volume_snapshot, "snapshot2_3"], \
                      [TestAction.start_vm, "vm1"], \
                      [TestAction.create_volume_snapshot, "vm1-root", "snapshot3_4"], \
                      [TestAction.stop_vm, "vm1"], \
                      [TestAction.start_vm, "vm1"], \
                      [TestAction.create_volume_snapshot, "vm1-root", "snapshot4_4"], \
                      [TestAction.delete_volume_snapshot, "snapshot1_1"], \
                      [TestAction.stop_vm, "vm1"], \
                      [TestAction.use_volume_snapshot, "snapshot4_2"], \
                      [TestAction.start_vm, "vm1"], \
                      [TestAction.stop_vm, "vm1"], \
                      [TestAction.use_volume_snapshot, "snapshot3_3"], \
                      [TestAction.start_vm, "vm1"], \
                      [TestAction.stop_vm, "vm1"], \
                      [TestAction.use_volume_snapshot, "snapshot4_4"], \
                      [TestAction.start_vm, "vm1"], \
                      [TestAction.stop_vm, "vm1"], \
                      [TestAction.use_volume_snapshot, "snapshot1_3"], \
                      [TestAction.start_vm, "vm1"], \
                      [TestAction.recover_global_config_sp_depth]
                     ])
