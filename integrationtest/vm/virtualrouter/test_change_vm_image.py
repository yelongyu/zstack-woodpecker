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
   vm = test_stub.create_basic_vm()
   test_obj_dict.add_vm(vm)
   vm.check()

   vm_uuid = vm.get_vm().uuid
   last_l3network_uuid = test_lib.lib_get_l3s_uuid_by_vm(vm.get_vm())
   last_primarystorage_uuid = test_lib.lib_get_root_volume(vm.get_vm()).primaryStorageUuid
   vm_ops.stop_vm(vm_uuid)
   image_uuid = test_lib.lib_get_image_by_name("ttylinux").uuid
   vm_ops.change_vm_image(vm_uuid,image_uuid)
   vm_ops.start_vm(vm_uuid)
   vm.update()
   #check whether the network config has changed
   l3network_uuid_after = test_lib.lib_get_l3s_uuid_by_vm(vm.get_vm())
   if l3network_uuid_after != last_l3network_uuid:
      test_util.test_fail('Change VM Image Failed.The Network config has changed.')
   #check whether primarystorage has changed
   primarystorage_uuid_after = test_lib.lib_get_root_volume(vm.get_vm()).primaryStorageUuid
   if primarystorage_uuid_after != last_primarystorage_uuid:
      test_util.test_fail('Change VM Image Failed.Primarystorage has changed.')
   #ping vm
   vm2 = test_stub.create_basic_vm()
   test_obj_dict.add_vm(vm2)
   vm2.check()
   cmd = "ping %s -c 4" % vm.get_vm().vmNics[0].ip
   rsp = test_lib.lib_execute_ssh_cmd(vm2.get_vm().vmNics[0].ip,'root','password',cmd,300)
   if isinstance(rsp,bool):
      if rsp == False:
         test_util.test_fail('Test Ping VM Failed')
   
   vm.destroy()
   vm2.destroy()
   test_util.test_pass('Change Vm Image Test Success')

def error_cleanup():
   global vm
   if vm:
      vm.destory()
