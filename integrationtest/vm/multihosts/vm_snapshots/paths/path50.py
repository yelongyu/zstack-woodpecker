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
		[TestAction.create_volume_snapshot, 'volume1', 'volume1-snapshot1'],
		[TestAction.create_volume_snapshot, 'vm1-root', 'vm1-root-snapshot2'],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot3'],
		[TestAction.create_volume_snapshot, 'volume3', 'volume3-snapshot7'],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot8'],
		[TestAction.create_volume_snapshot, 'vm1-root', 'vm1-root-snapshot12'],
		[TestAction.create_volume_snapshot, 'volume3', 'volume3-snapshot13'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.use_volume_snapshot, 'volume2-snapshot3'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.create_volume_snapshot, 'volume1', 'volume1-snapshot14'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.use_volume_snapshot, 'vm1-root-snapshot2'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.resize_volume, 'vm1', 5*1024*1024],
		[TestAction.delete_volume_snapshot, 'vm1-snapshot3'],
		[TestAction.delete_vm_snapshot, 'vm1-snapshot8'],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot15'],
		[TestAction.delete_vm_snapshot, 'vm1-snapshot15'],
])



'''
The final status:
Running:['vm1']
Stopped:[]
Enadbled:['volume1-snapshot1', 'vm1-root-snapshot2', 'volume1-snapshot3', 'volume2-snapshot3', 'volume3-snapshot3', 'volume3-snapshot7', 'vm1-root-snapshot12', 'volume3-snapshot13', 'volume1-snapshot14']
attached:['volume1', 'volume2', 'volume3']
Detached:[]
Deleted:['vm1-snapshot3', 'vm1-snapshot8', 'volume1-snapshot8', 'volume2-snapshot8', 'volume3-snapshot8', 'vm1-snapshot15', 'volume1-snapshot15', 'volume2-snapshot15', 'volume3-snapshot15']
Expunged:[]
Ha:[]
Group:
'''