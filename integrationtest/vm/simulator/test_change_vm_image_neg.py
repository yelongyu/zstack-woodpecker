'''

New Integration Test for changing vm image neg.

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
   image_uuid = test_lib.lib_get_image_by_name("centos").uuid
   vm = test_stub.create_vm(image_uuid = image_uuid)
   vm_uuid = vm.get_vm().uuid
   image_uuid = test_lib.lib_get_image_by_name("image_for_sg_test").uuid
   imagelist = vm_ops.get_image_candidates_for_vm_to_change(vm_uuid)
   for image in imagelist.inventories:
      #check whether the image is an iso
      if image.format == "iso" or image.url.endswith('.iso') or image.mediaType == 'ISO':
         test_util.test_fail("iso cannot be chose.")
      #check whether the image is a vr image
      if image.system == "true":
         test_util.test_fail("vr image cannot be chose.")
   #test change vm image when vm is running	 
   try:
      vm_ops.change_vm_image(vm_uuid,image_uuid)
   except:
      vm.destroy()
      vm.expunge()
      test_util.test_pass('Neg Test Change VM Image Function Success')
   test_util.test_fail('Neg Test Change VM Image Function Failed')
def error_cleanup():
   global vm
   if vm:
      vm.destroy()
