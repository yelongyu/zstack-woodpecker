import zstackwoodpecker.test_state as ts_header
TestAction = ts_header.TestAction
def path():
    return dict(initial_formation="template6", \
           path_list=[
                      [TestAction.stop_vm, "vm1"], \
                      [TestAction.start_vm, "vm1"]
                     ])
