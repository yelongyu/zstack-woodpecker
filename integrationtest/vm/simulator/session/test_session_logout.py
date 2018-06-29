'''

New Test After session logout

@author: quarkonics
'''
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.operations.account_operations as acc_ops
import zstackwoodpecker.operations.vm_operations as vm_ops
import apibinding.inventory as inventory
import threading
import uuid
import os

test_stub = test_lib.lib_get_test_stub()

def test():
   session_uuid = acc_ops.login_as_admin()
   acc_ops.logout(session_uuid)
   
   image_name = os.environ.get('imageName3')
   image_uuid = test_lib.lib_get_image_by_name(image_name).uuid
   try:
       vm = test_stub.create_vm(image_uuid = image_uuid, session_uuid=session_uuid)
       test_util.test_fail('Expect exception after logout while there is none')
   except:
       pass

   vm = test_stub.create_vm(image_uuid = image_uuid)
   vm_ops.stop_vm(vm.get_vm().uuid)
   vm_ops.start_vm(vm.get_vm().uuid)
   try:
       vm_ops.stop_vm(vm.get_vm().uuid, session_uuid=session_uuid)
       test_util.test_fail('Expect exception after logout while there is none')
   except:
       pass
   vm.destroy()
   vm.expunge()
   test_util.test_pass('Test operations after session logout passed')
