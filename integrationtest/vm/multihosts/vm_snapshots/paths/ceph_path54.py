import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", checking_point=8, path_list=[
		[TestAction.create_vm, 'vm1', ],
		[TestAction.create_volume, 'volume1', 'flag=scsi'],
		[TestAction.attach_volume, 'vm1', 'volume1'],
		[TestAction.create_volume, 'volume2', 'flag=scsi'],
		[TestAction.attach_volume, 'vm1', 'volume2'],
		[TestAction.create_volume, 'volume3', 'flag=scsi'],
		[TestAction.attach_volume, 'vm1', 'volume3'],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot1'],
		[TestAction.clone_vm, 'vm1', 'vm2', 'full'],
		[TestAction.resize_data_volume, 'volume1', 5*1024*1024],
		[TestAction.create_vm_snapshot, 'vm2', 'vm2-snapshot5'],
		[TestAction.batch_delete_volume_snapshot, ['vm1-snapshot1','clone@volume2-snapshot5',]],
		[TestAction.create_vm_snapshot, 'vm2', 'vm2-snapshot9'],
		[TestAction.create_volume_snapshot, 'vm1-root', 'vm1-root-snapshot13'],
		[TestAction.delete_volume_snapshot, 'vm2-snapshot9'],
		[TestAction.batch_delete_volume_snapshot, ['clone@volume2-snapshot9','volume3-snapshot1',]],
		[TestAction.create_vm_snapshot, 'vm2', 'vm2-snapshot14'],
		[TestAction.delete_vm_snapshot, 'vm2-snapshot14'],
])



'''
The final status:
Running:['vm1', 'vm2']
Stopped:[]
Enadbled:['volume1-snapshot1', 'volume2-snapshot1', 'vm2-snapshot5', 'clone@volume1-snapshot5', 'clone@volume3-snapshot5', 'clone@volume1-snapshot9', 'clone@volume3-snapshot9', 'vm1-root-snapshot13']
attached:['volume1', 'volume2', 'volume3', 'clone@volume1', 'clone@volume2', 'clone@volume3']
Detached:[]
Deleted:['vm1-snapshot1', 'clone@volume2-snapshot5', 'vm2-snapshot9', 'clone@volume2-snapshot9', 'volume3-snapshot1', 'vm2-snapshot14', 'clone@volume1-snapshot14', 'clone@volume2-snapshot14', 'clone@volume3-snapshot14']
Expunged:[]
Ha:[]
Group:
'''
