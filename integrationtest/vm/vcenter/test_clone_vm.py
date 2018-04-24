import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import os
import test_stub


test_obj_dict = test_state.TestStateDict()

def test():

  l3_vr_network = os.environ['l3vCenterNoVlanNetworkName']
  image_name = os.environ['image_dhcp_name']

  vm = test_stub.create_vm_in_vcenter(vm_name='vm', image_name = image_name, l3_name=l3_vr_network)
  test_obj_dict.add_vm(vm)
  vm.check()
  
  clone_vm = vm.clone(['clone_vm'])[0]
  test_obj_dict.add_vm(clone_vm)
  clone_vm.check()

  names = []
  for i in range(5):
    names.append('clone' + str(i+1))

  clone_vms = clone_vm.clone(names)

  for _vm in clone_vms:
    _vm.check()
    test_obj_dict.add_vm(_vm)

  test_lib.lib_error_cleanup(test_obj_dict)
  test_util.test_pass("test vcenter clone vm pass")




def error_cleanup():
  test_lib.lib_error_cleanup(test_obj_dict)
