'''
Integration Test for changing vm image from linux to windows in virtualrouter.

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
   primary_storage_list = res_ops.query_resource(res_ops.PRIMARY_STORAGE)
   for ps in primary_storage_list:
       if ps.type == "SharedBlock":
           test_util.test_skip('SharedBlock primary storage does not support overProvision')
   global vm
   #set overProvisioning.primaryStorage's value as 10
   con_ops.change_global_config('mevoco','overProvisioning.primaryStorage',10)
   test_lib.lib_create_disk_offering(diskSize=1099511627776,name="1T")
   l3_uuid = test_lib.lib_get_l3_by_name("l3VlanNetwork1").uuid
   image_uuid = test_lib.lib_get_image_by_name("ttylinux").uuid
   disk_offering_uuids = [test_lib.lib_get_disk_offering_by_name("smallDiskOffering").uuid,test_lib.lib_get_disk_offering_by_name("root-disk").uuid,test_lib.lib_get_disk_offering_by_name("1T").uuid]
   #choose the ps which availableCapacity >= 105G
   cond = res_ops.gen_query_conditions('availableCapacity', '>=', '112742891520')
   ps_uuid = res_ops.query_resource(res_ops.PRIMARY_STORAGE, cond)[0].uuid
   system_tag = "primaryStorageUuidForDataVolume::%s" % ps_uuid
   vm = test_stub.create_vm(l3_uuid_list = [l3_uuid],image_uuid = image_uuid,vm_name="test-vm",disk_offering_uuids = disk_offering_uuids,system_tags=[system_tag])
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
   vr = test_lib.lib_find_vr_by_vm(vm.get_vm())[0]
   vr_mgmt_ip = test_lib.lib_find_vr_mgmt_ip(vr)
   #stop vm's vr
   vm_ops.stop_vm(vr.uuid)
   #change vm image
   image_uuid = test_lib.lib_get_image_by_name("windows").uuid
   vm_ops.change_vm_image(vm_uuid,image_uuid)
   #check whether vr's status is running
   if vr.applianceVmType == 'vrouter':
      if not test_lib.lib_wait_target_up(vr_mgmt_ip,'7272',240):
         test_util.test_fail('vm:%s is not startup in 240 seconds.Fail to reboot it.' % vr.uuid)
      time.sleep(20)
   else:
      vm_ops.start_vm(vr.uuid)
      vm_ops.reconnect_vr(vr.uuid)
   vm_ops.start_vm(vm_uuid)
   vm.update()
   #check whether the windows vm is running successfully
   vm_ip = vm.get_vm().vmNics[0].ip
   if not test_lib.lib_wait_target_up(vm_ip,'23',1200):
      test_util.test_fail('vm:%s is not startup in 1200 seconds.Fail to reboot it.' % vm_uuid)
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

   #check whether the linux vm is running successfully
   vm_ops.stop_vm(vm_uuid)
   #stop vm's vr
   vm_ops.stop_vm(vr.uuid)
   image_uuid = test_lib.lib_get_image_by_name("image_for_sg_test").uuid
   vm_ops.change_vm_image(vm_uuid,image_uuid)
   #check whether vr's status is running
   if vr.applianceVmType == 'vrouter':
      if not test_lib.lib_wait_target_up(vr_mgmt_ip,'7272',240):
         test_util.test_fail('vm:%s is not startup in 240 seconds.Fail to reboot it.' % vr.uuid)
      time.sleep(20)
   else:
      vm_ops.start_vm(vr.uuid)
      vm_ops.reconnect_vr(vr.uuid)
   vm_ops.start_vm(vm_uuid)

   if not test_lib.lib_wait_target_up(vm_ip,'22',180):
      test_util.test_fail('vm:%s is not startup in 180 seconds.Fail to reboot it.' % vm_uuid)
   #check whether data volumes attached to the vm has changed
   data_volumes_after_uuids_linux = []
   data_volumes_after_linux = test_lib.lib_get_data_volumes(vm.get_vm())
   for data_volume in data_volumes_after_linux:
      data_volumes_after_uuids_linux.append(data_volume.uuid)
   if set(data_volumes_after_uuids) != set(data_volumes_after_uuids_linux):
      test_util.test_fail('Change Vm Image Failed.Data volumes changed.')
   #check whether the network config has changed
   l3network_uuid_after_linux = test_lib.lib_get_l3s_uuid_by_vm(vm.get_vm())
   if l3network_uuid_after != l3network_uuid_after_linux:
      test_util.test_fail('Change VM Image Failed.The Network config has changed.')
   #check whether primarystorage has changed
   primarystorage_uuid_after_linux = test_lib.lib_get_root_volume(vm.get_vm()).primaryStorageUuid
   if primarystorage_uuid_after_linux != primarystorage_uuid_after:
      test_util.test_fail('Change VM Image Failed.Primarystorage has changed.')

   test_lib.lib_destroy_vm_and_data_volumes(vm.get_vm())
   test_util.test_pass('Change Vm Image Test Success')

def error_cleanup():
   global vm
   if vm:
      vm.destroy()
