import zstackwoodpecker.test_state as ts_header
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", path_list=[
	[TestAction.create_vm_backup, "vm1", "backup-vm1"],
	[TestAction.stop_vm, "vm1"],
	[TestAction.use_vm_backup, "backup-vm1"],
	[TestAction.start_vm, "vm1"]])
