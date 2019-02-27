import zstackwoodpecker.test_state as ts_header
TestAction = ts_header.TestAction
def path():
    return dict(initial_formation="template1", \
           path_list=[[TestAction.create_volume_snapshot, "vm1-root", "snapshot1"], \
                      [TestAction.stop_vm, "vm1"], \
                      [TestAction.reinit_vm, "vm1"], \
                      [TestAction.start_vm, "vm1"], \
                      [TestAction.stop_vm, "vm1"], \
                      [TestAction.reinit_vm, "vm1"], \
                      [TestAction.start_vm, "vm1"], \
                      [TestAction.batch_delete_volume_snapshot, ["snapshot1"]]
                     ])
