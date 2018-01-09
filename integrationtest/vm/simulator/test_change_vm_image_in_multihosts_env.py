'''
New Integration Test for changing vm image.

@author: Xiaoshuang
'''

import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.operations.vm_operations as vm_ops
import zstackwoodpecker.operations.host_operations as host_ops

import time

vm = None
test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def test():
   test_util.test_dsc('Test Change VM Image In Multihosts Env')
   global vm
   image = test_lib.lib_get_image_by_name("centos")
   vm = test_stub.create_vm(image_uuid=image.uuid)
   last_l3network_uuid = test_lib.lib_get_l3s_uuid_by_vm(vm.get_vm())
   last_primarystorage_uuid = test_lib.lib_get_root_volume(vm.get_vm()).primaryStorageUuid
   last_host_uuid = test_lib.lib_get_vm_last_host(vm.get_vm()).uuid
   image_uuid = test_lib.lib_get_image_by_name("image_for_sg_test").uuid
   vm_uuid = vm.get_vm().uuid
   host_ops.change_host_state(host_uuid = last_host_uuid, state = 'disable')
   vm_ops.stop_vm(vm_uuid)
   ps = test_lib.lib_get_primary_storage_by_vm(vm.get_vm())
   #Disable vm's host.If ps is shared storage,the vm will be started on another host that meets the conditions and the operation of changing vm image will success.
   if ps.type != 'LocalStorage':
      vm_ops.change_vm_image(vm_uuid,image_uuid)
      vm_ops.start_vm(vm_uuid)
      #check whether the network config has changed
      l3network_uuid_after = test_lib.lib_get_l3s_uuid_by_vm(vm.get_vm())
      if l3network_uuid_after != last_l3network_uuid:
         test_util.test_fail('Change VM Image Failed.The Network config has changed.')
      #check whether primarystorage has changed
      primarystorage_uuid_after = test_lib.lib_get_root_volume(vm.get_vm()).primaryStorageUuid
      if primarystorage_uuid_after != last_primarystorage_uuid:
         test_util.test_fail('Change VM Image Failed.Primarystorage has changed.')
      vm.destroy()
      test_util.test_pass('Change Vm Image Test Success In Multihosts Env Success')
   #Disable vm's host.If ps is local storage,the operation of changing vm image will fail.  
   else:
      try:
         vm_ops.change_vm_image(vm_uuid, image_uuid)
      except:
         test_util.test_pass('Change Vm Image Test Success In Multihosts Env Success')
   test_util.test_fail('Test Change VM Image In Multihosts Env Success Failed')

def error_cleanup():
   global vm
   if vm:
      vm.destroy()
