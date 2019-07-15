import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", path_list=[
		[TestAction.create_vm, 'vm1', ],
		[TestAction.create_volume, 'volume1', 'flag=scsi'],
		[TestAction.attach_volume, 'vm1', 'volume1'],
		[TestAction.create_volume, 'volume2', 'flag=scsi'],
		[TestAction.attach_volume, 'vm1', 'volume2'],
		[TestAction.create_volume, 'volume3', 'flag=scsi'],
		[TestAction.attach_volume, 'vm1', 'volume3'],
		[TestAction.clone_volume, 'vm1', 'clone-vm1'],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot1'],
		[TestAction.reboot_vm, 'vm1'],
		[TestAction.clone_volume, 'vm1', 'clone-vm1'],
		[TestAction.create_vm_snapshot, 'clone-vm1', 'clone-vm1-snapshot5'],
		[TestAction.stop_vm, 'clone-vm1'],
		[TestAction.use_vm_snapshot, 'clone-vm1-snapshot5'],
		[TestAction.start_vm, 'clone-vm1'],
])



'''
The final status:
Running:['vm1', 'clone-vm1', 'clone-vm1']
Stopped:[]
Enadbled:['vm1-snapshot1', 'volume1-snapshot1', 'volume2-snapshot1', 'volume3-snapshot1', 'clone-vm1-snapshot5']
attached:['volume1', 'volume2', 'volume3']
Detached:[]
Deleted:[]
Expunged:[]
Ha:[]
Group:
	vm_snap2:['clone-vm1-snapshot5']---clone-vm1
	vm_snap1:['vm1-snapshot1', 'volume1-snapshot1', 'volume2-snapshot1', 'volume3-snapshot1']---vm1volume1_volume2_volume3
'''