'''

@author: Youyk
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.zstack_test.zstack_test_vm as zstack_test_vm
import zstackwoodpecker.header.vm as vm_header
import os

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def test():
    global test_obj_dict
    test_util.test_dsc('Create test vm and check')

    vm = test_stub.create_vlan_vm()
    test_obj_dict.add_vm(vm)
    vm.check()

    test_util.test_dsc('Create volume and check')
    volume = test_stub.create_volume()

    vr_vm = test_lib.lib_find_vr_by_vm(vm.vm)[0]
    test_vr_vm = zstack_test_vm.ZstackTestVm()
    test_vr_vm.vm = vr_vm
    test_vr_vm.state = vm_header.RUNNING

    volume.attach(vm)
    volume.check()

    volume.detach()
    volume.check()

    test_util.test_dsc('Attach volume to VR vm and check')
    volume.attach(test_vr_vm)
    volume.check()

    volume.detach()
    volume.check()

    volume.delete()
    volume.check()
    vm.destroy()
    test_util.test_pass('Create Data Volume for Vlan VirtualRouter Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)
