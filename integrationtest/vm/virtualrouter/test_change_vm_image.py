'''

New Integration Test for changing vm image.

@author: Xiaoshuang
'''

import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.operations.vm_operations as vm_ops
import zstackwoodpecker.operations.config_operations as con_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import time
vm = None
test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def test():
   test_util.test_dsc('Test Change VM Image Function')
   #set overProvisioning.primaryStorage's value as 10
   primary_storage_list = res_ops.query_resource(res_ops.PRIMARY_STORAGE)
   for ps in primary_storage_list:
       if ps.type == "SharedBlock" or ps.type == "AliyunEBS":
           test_util.test_skip('SharedBlock/AliyunEBS primary storage does not support overProvision')
   con_ops.change_global_config('mevoco','overProvisioning.primaryStorage',10)
   global vm
   test_lib.lib_create_disk_offering(diskSize=1099511627776,name="1T")
   l3_uuid = test_lib.lib_get_l3_by_name("l3VlanNetwork3").uuid
   image_uuid = test_lib.lib_get_image_by_name("ttylinux").uuid
   disk_offering_uuids = [test_lib.lib_get_disk_offering_by_name("smallDiskOffering").uuid,test_lib.lib_get_disk_offering_by_name("root-disk").uuid,test_lib.lib_get_disk_offering_by_name("1T").uuid]
   vm = test_stub.create_vm(l3_uuid_list = [l3_uuid],image_uuid = image_uuid,vm_name="test-nxs",disk_offering_uuids = disk_offering_uuids)
   test_obj_dict.add_vm(vm)
   vm.check()

   vm_uuid = vm.get_vm().uuid
   last_data_volumes_uuids = []
   last_data_volumes = test_lib.lib_get_data_volumes(vm.get_vm())
   for data_volume in last_data_volumes:
        last_data_volumes_uuids.append(data_volume.uuid)
   last_l3network_uuid = test_lib.lib_get_l3s_uuid_by_vm(vm.get_vm())
   last_primarystorage_uuid = test_lib.lib_get_root_volume(vm.get_vm()).primaryStorageUuid

   ps = test_lib.lib_get_primary_storage_by_uuid(last_primarystorage_uuid)
   avail_cap = ps.availableCapacity
   total_cap = ps.totalCapacity

   vm_ops.stop_vm(vm_uuid)
   vr = test_lib.lib_find_vr_by_vm(vm.get_vm())[0]
   vr_mgmt_ip = test_lib.lib_find_vr_mgmt_ip(vr)
   #stop vm's vr
   vm_ops.stop_vm(vr.uuid)
   image_uuid = test_lib.lib_get_image_by_name("image_for_sg_test").uuid
   vm_ops.change_vm_image(vm_uuid,image_uuid)
   #check whether vr's status is running
   if vr.applianceVmType == 'vrouter':
      if not test_lib.lib_wait_target_up(vr_mgmt_ip,'7272',240):
         test_util.test_fail('vm:%s is not startup in 240 seconds.Fail to reboot it.' % vr.uuid)
      time.sleep(20)
   #if vr.state == 'Stopped':
   else:
      vm_ops.start_vm(vr.uuid)
      vm_ops.reconnect_vr(vr.uuid)
   vm_ops.start_vm(vm_uuid)
   vm.update()
   #check whether the vm is running successfully
   if not test_lib.lib_wait_target_up(vm.get_vm().vmNics[0].ip,'22',120):
      test_util.test_fail('vm:%s is not startup in 120 seconds.Fail to reboot it.' % vm_uuid)
   #check whether data volumes attached to the vm has changed
   data_volumes_after_uuids = []
   data_volumes_after = test_lib.lib_get_data_volumes(vm.get_vm())
   for data_volume in data_volumes_after:
      data_volumes_after_uuids.append(data_volume.uuid)
   if set(last_data_volumes_uuids) != set(data_volumes_after_uuids):
      test_util.test_fail('Change Vm Image Failed.Data volumes changed.')
   #check whether the network config has changed
   l3network_uuid_after = test_lib.lib_get_l3s_uuid_by_vm(vm.get_vm())
   if set(l3network_uuid_after) != set(last_l3network_uuid):
      test_util.test_fail('Change VM Image Failed.The Network config has changed.')
   #check whether primarystorage has changed
   primarystorage_uuid_after = test_lib.lib_get_root_volume(vm.get_vm()).primaryStorageUuid
   if primarystorage_uuid_after != last_primarystorage_uuid:
      test_util.test_fail('Change VM Image Failed.Primarystorage has changed.')

   ps = test_lib.lib_get_primary_storage_by_uuid(primarystorage_uuid_after)
   avail_cap1 = ps.availableCapacity
   total_cap1 = ps.totalCapacity

   if total_cap != total_cap1:
      test_util.test_fail('Primary Storage total capacity is not same,after changing vm image:%s.The previous value:%s, the current value:%s' % (image_uuid,total_cap,total_cap1))
   if avail_cap <= avail_cap1:
      test_util.test_fail('Primary Storage available capacity is not correct,after changing larger image:%s.The previous value:%s, the current value:%s' % (image_uuid,avail_cap,avail_cap1))

   vm_ops.stop_vm(vm_uuid)
   #stop vm's vr
   vm_ops.stop_vm(vr.uuid)
   image_tiny_uuid = test_lib.lib_get_image_by_name("ttylinux").uuid
   vm_ops.change_vm_image(vm_uuid,image_tiny_uuid)
   #check whether vr's status is running
   if vr.applianceVmType == 'vrouter':
      if not test_lib.lib_wait_target_up(vr_mgmt_ip,'7272',240):
         test_util.test_fail('vm:%s is not startup in 240 seconds.Fail to reboot it.' % vr.uuid)
      time.sleep(20)
   #if vr.state == 'Stopped':
   else:
      vm_ops.start_vm(vr.uuid)
      vm_ops.reconnect_vr(vr.uuid)
   vm_ops.start_vm(vm_uuid)
   vm.update()
   #check whether the vm is running successfully
   if not test_lib.lib_wait_target_up(vm.get_vm().vmNics[0].ip,'22',120):
      test_util.test_fail('vm:%s is not startup in 120 seconds.Fail to reboot it.' % vm_uuid)
   #check whether data volumes attached to the vm has changed
   data_volumes_after_uuids_tiny = []
   data_volumes_after_tiny = test_lib.lib_get_data_volumes(vm.get_vm())
   for data_volume in data_volumes_after_tiny:
      data_volumes_after_uuids_tiny.append(data_volume.uuid)
   if set(data_volumes_after_uuids_tiny) != set(data_volumes_after_uuids):
      test_util.test_fail('Change Vm Image Failed.Data volumes changed.')
   #check whether the network config has changed
   l3network_uuid_after_tiny = test_lib.lib_get_l3s_uuid_by_vm(vm.get_vm())
   if set(l3network_uuid_after_tiny) != set(l3network_uuid_after_tiny):
      test_util.test_fail('Change VM Image Failed.The Network config has changed.')
   #check whether primarystorage has changed
   primarystorage_uuid_after_tiny = test_lib.lib_get_root_volume(vm.get_vm()).primaryStorageUuid
   if primarystorage_uuid_after != primarystorage_uuid_after_tiny:
      test_util.test_fail('Change VM Image Failed.Primarystorage has changed.')

   ps = test_lib.lib_get_primary_storage_by_uuid(primarystorage_uuid_after_tiny)
   avail_cap2 = ps.availableCapacity
   total_cap2 = ps.totalCapacity

   if total_cap2 != total_cap1:
      test_util.test_fail('Primary Storage total capacity is not same,after changing vm image:%s.The previous value:%s, the current value:%s' % (image_uuid,total_cap1,total_cap2))
   if avail_cap2 <= avail_cap1:
      test_util.test_fail('Primary Storage available capacity is not correct,after changing smaller image:%s.The previous value:%s, the current value:%s' % (image_uuid,avail_cap1,avail_cap2))


   test_lib.lib_destroy_vm_and_data_volumes(vm.get_vm())
   test_util.test_pass('Change Vm Image Test Success')

def error_cleanup():
   global vm
   if vm:
      vm.destroy()
