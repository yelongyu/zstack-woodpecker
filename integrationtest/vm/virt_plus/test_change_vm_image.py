'''

New Integration Test for changing vm image.

@author: Xiaoshuang
'''
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.operations.vm_operations as vm_ops

vm = None
test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def test():
   test_util.test_dsc('Test Change VM Image Function')
   global vm
   disk_offering_uuids = [test_lib.lib_get_disk_offering_by_name("smallDiskOffering").uuid,test_lib.lib_get_disk_offering_by_name("root-disk").uuid]
   vm = test_stub.create_vm(image_name = "ttylinux",vm_name="test-nxs",disk_offering_uuids = disk_offering_uuids)
   test_obj_dict.add_vm(vm)
   vm.check()

   vm_uuid = vm.get_vm().uuid
   last_data_volumes_uuids = []
   last_data_volumes = test_lib.lib_get_data_volumes(vm.get_vm())
   for data_volume in last_data_volumes:
        last_data_volumes_uuids.append(data_volume.uuid)
   last_l3network_uuid = test_lib.lib_get_l3s_uuid_by_vm(vm.get_vm())
   last_primarystorage_uuid = test_lib.lib_get_root_volume(vm.get_vm()).primaryStorageUuid
   vm_ops.stop_vm(vm_uuid)
   image_uuid = test_lib.lib_get_image_by_name("image_for_sg_test").uuid
   vm_ops.change_vm_image(vm_uuid,image_uuid)
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
   if l3network_uuid_after != last_l3network_uuid:
      test_util.test_fail('Change VM Image Failed.The Network config has changed.')
   #check whether primarystorage has changed
   primarystorage_uuid_after = test_lib.lib_get_root_volume(vm.get_vm()).primaryStorageUuid
   if primarystorage_uuid_after != last_primarystorage_uuid:
      test_util.test_fail('Change VM Image Failed.Primarystorage has changed.')

   test_lib.lib_destroy_vm_and_data_volumes(vm.get_vm())
   vm.expunge()
   test_util.test_pass('Change Vm Image Test Success')

def error_cleanup():
   global vm
   if vm:
      vm.destory()

