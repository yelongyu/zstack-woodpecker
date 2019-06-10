import zstackwoodpecker.test_state as ts_header
TestAction = ts_header.TestAction
def path():
    return dict(repeat=5000, initial_formation="template5", path_list=[
        [TestAction.add_image, "image1", 'root', "http://172.20.1.28/mirror/diskimages/centos7-test.qcow2"],
        [TestAction.delete_image, "image1"],
        [TestAction.recover_image, "image1"],
        [TestAction.delete_image, "image1"],
        [TestAction.expunge_image, "image1"]])
