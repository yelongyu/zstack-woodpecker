import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", path_list=[
		[TestAction.create_vm, 'vm1', 'flag=ceph'],
		[TestAction.create_volume, 'volume1', 'flag=ceph,scsi'],
		[TestAction.attach_volume, 'vm1', 'volume1'],
		[TestAction.create_volume, 'volume2', 'flag=ceph,scsi'],
		[TestAction.attach_volume, 'vm1', 'volume2'],
		[TestAction.create_volume, 'volume3', 'flag=ceph,scsi'],
		[TestAction.attach_volume, 'vm1', 'volume3'],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot1'],
		[TestAction.stop_vm, 'vm1'],
		[TestAction.reinit_vm, 'vm1'],
		[TestAction.start_vm, 'vm1'],
		[TestAction.resize_data_volume, 'volume3', 5*1024*1024],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot5'],
		[TestAction.create_image_from_volume, 'vm1', 'vm1-image1'],
		[TestAction.create_vm_snapshot, 'vm1', 'vm1-snapshot9'],
		[TestAction.resize_volume, 'vm1', 5*1024*1024],
		[TestAction.create_volume, 'volume4', 'flag=ceph,scsi'],
		[TestAction.attach_volume, 'vm1', 'volume4'],
		[TestAction.batch_delete_volume_snapshot, ['vm1-snapshot5','volume1-snapshot1',]],
		[TestAction.delete_vm_snapshot, 'vm1-snapshot9'],
])



'''
The final status:
Running:['vm1']
Stopped:[]
Enadbled:['vm1-snapshot1', 'volume2-snapshot1', 'volume3-snapshot1', 'volume1-snapshot5', 'volume2-snapshot5', 'volume3-snapshot5', 'vm1-image1']
attached:['volume1', 'volume2', 'volume3', 'volume4']
Detached:[]
Deleted:['vm1-snapshot5', 'volume1-snapshot1', 'vm1-snapshot9', 'volume1-snapshot9', 'volume2-snapshot9', 'volume3-snapshot9']
Expunged:[]
Ha:[]
Group:
'''