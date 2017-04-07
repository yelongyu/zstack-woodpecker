'''
New Integration Test for detaching vm network, migrate and attaching network.
@author: SyZhao
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.volume_operations as vol_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.net_operations as net_ops
import zstackwoodpecker.zstack_test.zstack_test_vm as test_vm_header
import time
import os

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def test():
    global test_obj_dict

    pss = res_ops.get_resource(res_ops.PRIMARY_STORAGE)
    if pss[0].type != "LocalStorage":
        test_util.test_skip("this test is designed to run on localstorage, skip on other ps type.")    

    vm = test_stub.create_vr_vm('vm1', 'imageName_net', 'l3VlanNetwork3')
    test_obj_dict.add_vm(vm)
    vm.check()

    vm_nic_uuid = vm.vm.vmNics[0].uuid
    net_ops.detach_l3(vm_nic_uuid)

    vm.stop()
    vm.check()

    #test_stub.migrate_vm_to_random_host(vm)
    target_host = test_lib.lib_find_random_host(vm.vm)
    vol_ops.migrate_volume(vm.get_vm().allVolumes[0].uuid, target_host.uuid)

    l3_name = os.environ.get('l3VlanNetwork3')
    l3_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid

    net_ops.attach_l3(l3_uuid, vm.vm.uuid)

    vm.start()
    vm.check()

    test_util.test_pass('test detach l3, migrate and attaching passed.')



#Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)
