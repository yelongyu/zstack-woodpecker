import zstackwoodpecker.test_state as ts_header
TestAction = ts_header.TestAction
def path():
    return dict(initial_formation="template1", \
           path_list=[
                      [TestAction.add_image, "sftp", "image1", "qcow2", "file:///opt/zstack-dvd/zstack-image-1.4.qcow2"], \
                      [TestAction.create_vm_by_image, "image1", "vm1"], \
                      [TestAction.stop_vm, "vm1"], \
                      [TestAction.start_vm, "vm1"]
                     ])
