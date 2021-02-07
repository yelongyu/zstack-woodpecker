'''

New Integration Test for changing vm image.

@author: Xiaoshuang
'''
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.operations.vm_operations as vm_ops
import zstackwoodpecker.operations.config_operations as con_ops
vm = None
test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def test():
   test_util.test_dsc('Test Change VM Image Function')
   #set overProvisioning.primaryStorage's value as 10
   con_ops.change_global_config('mevoco','overProvisioning.primaryStorage',10)
   global vm
   test_lib.lib_create_disk_offering(diskSize=107374182400,name="100G")
   disk_offering_uuids = [test_lib.lib_get_disk_offering_by_name("smallDiskOffering").uuid,test_lib.lib_get_disk_offering_by_name("root-disk").uuid,test_lib.lib_get_disk_offering_by_name("100G").uuid]
   vm = test_stub.create_vm(image_name = "ttylinux",vm_name="test-vm",disk_offering_uuids = disk_offering_uuids)
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
   image = test_lib.lib_get_image_by_name("image_for_sg_test")
   image_uuid = image.uuid
   image_tiny = test_lib.lib_get_image_by_name("ttylinux")
   image_tiny_uuid = image_tiny.uuid
   change_size = (image.size-image_tiny.size)/10

   vm_ops.change_vm_image(vm_uuid,image_uuid)
   vm_ops.start_vm(vm_uuid)
   vm.update()
   #check whether the vm is running successfully
   if not test_lib.lib_wait_target_up(vm.get_vm().vmNics[0].ip,'22',180):
      test_util.test_fail('vm:%s is not startup in 180 seconds.Fail to reboot it.' % vm_uuid)
   #check whether data volumes attached to the vm has changed
   data_volumes_after_uuids = []
   data_volumes_after = test_lib.lib_get_data_volumes(vm.get_vm())
   for data_volume in data_volumes_after:
      data_volumes_after_uuids.append(data_volume.uuid)
   if set(last_data_volumes_uuids) != set(data_volumes_after_uuids):
      test_util.test_fail('Change Vm Image Failed.Data volumes changed.')
   #check whether the network config has changed
   l3network_uuid_after = test_lib.lib_get_l3s_uuid_by_vm(vm.get_vm())
   if l3network_uuid_after != last_l3network_uuid:
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
   if not (avail_cap1-1) <= (avail_cap - change_size) <= (avail_cap1+1):
      test_util.test_fail('Primary Storage available capacity is not correct,after changing larger image:%s.The previous value:%s, the current value:%s' % (image_uuid,avail_cap,avail_cap1))

   vm_ops.stop_vm(vm_uuid)
   image_tiny_uuid = image_tiny.uuid
   vm_ops.change_vm_image(vm_uuid,image_tiny_uuid)
   vm_ops.start_vm(vm_uuid)
   vm.update()
   #check whether the vm is running successfully
   if not test_lib.lib_wait_target_up(vm.get_vm().vmNics[0].ip,'22',180):
      test_util.test_fail('vm:%s is not startup in 180 seconds.Fail to reboot it.' % vm_uuid)
   #check whether data volumes attached to the vm has changed
   data_volumes_after_uuids_tiny = []
   data_volumes_after_tiny = test_lib.lib_get_data_volumes(vm.get_vm())
   for data_volume in data_volumes_after_tiny:
      data_volumes_after_uuids_tiny.append(data_volume.uuid)
   if set(data_volumes_after_uuids_tiny) != set(data_volumes_after_uuids):
      test_util.test_fail('Change Vm Image Failed.Data volumes changed.')
   #check whether the network config has changed
   l3network_uuid_after_tiny = test_lib.lib_get_l3s_uuid_by_vm(vm.get_vm())
   if l3network_uuid_after_tiny != l3network_uuid_after:
      test_util.test_fail('Change VM Image Failed.The Network config has changed.')
   #check whether primarystorage has changed
   primarystorage_uuid_after_tiny = test_lib.lib_get_root_volume(vm.get_vm()).primaryStorageUuid
   if primarystorage_uuid_after_tiny != primarystorage_uuid_after:
      test_util.test_fail('Change VM Image Failed.Primarystorage has changed.')

   ps = test_lib.lib_get_primary_storage_by_uuid(primarystorage_uuid_after_tiny)
   avail_cap2 = ps.availableCapacity
   total_cap2 = ps.totalCapacity

   if total_cap2 != total_cap1:
      test_util.test_fail('Primary Storage total capacity is not same,after changing vm image:%s.The previous value:%s, the current value:%s' % (image_tiny_uuid,total_cap1,total_cap2))
   if not (change_size-1)<=(avail_cap2 - avail_cap1)<= (change_size+1):
      test_util.test_fail('Primary Storage available capacity is not correct,after changing smaller image:%s.The previous value:%s, the current value:%s' % (image_tiny_uuid,avail_cap1,avail_cap2))



   test_lib.lib_destroy_vm_and_data_volumes(vm.get_vm())
   vm.expunge()
   test_util.test_pass('Change Vm Image Test Success')

def error_cleanup():
   global vm
   if vm:
      vm.destroy()
