import zstackwoodpecker.test_state as ts_header
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", path_list=[
        [TestAction.create_mini_vm, "vm1", 'data_volume=true', 'cpu=random', 'memory=random', 'provisiong=thick'],
        [TestAction.delete_vm, 'vm1'],
        [TestAction.recover_vm, 'vm1'],
        [TestAction.create_vm_by_image, "iso1", "iso", "vm2"],
        [TestAction.change_vm_ha, 'vm1'],
        [TestAction.change_vm_ha, 'vm1']])