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
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot1'],
		[TestAction.create_image_from_volume, 'vm1', 'vm1-image1'],
		[TestAction.detach_volume, 'volume2'],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot5'],
		[TestAction.clone_vm, 'vm1', 'vm2'],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot8'],
		[TestAction.create_image_from_volume, 'vm2', 'vm2-image2'],
		[TestAction.delete_volume, 'volume3'],
		[TestAction.batch_delete_volume_snapshot, ['volume3-snapshot1','volume3-snapshot8',]],
		[TestAction.delete_vm_snapshot, 'vm1-snapshot5'],
])



'''
The final status:
Running:['vm1', 'vm2']
Stopped:[]
Enadbled:['vm1-snapshot1', 'volume1-snapshot1', 'volume2-snapshot1', 'vm1-snapshot8', 'volume1-snapshot8', 'vm1-image1', 'vm2-image2']
attached:['volume1']
Detached:['volume2']
Deleted:['volume3', 'volume3-snapshot1', 'volume3-snapshot8', 'vm1-snapshot5', 'volume1-snapshot5', 'volume3-snapshot5']
Expunged:[]
Ha:[]
Group:
'''