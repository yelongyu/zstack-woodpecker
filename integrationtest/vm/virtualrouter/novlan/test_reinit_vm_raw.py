'''

New Integration Test for reinit VM.

@author: quarkonics
'''

import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import os

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def test():
    image_name = os.environ.get('imageName_s')
    image_uuid = test_lib.lib_get_image_by_name(image_name).uuid
    l3_name = os.environ.get('l3NoVlanNetworkName1')

    ps = res_ops.query_resource(res_ops.PRIMARY_STORAGE)
    for i in ps:
        if i.type == 'AliyunEBS':
            test_util.test_skip('Skip vm reinit test on AliyunEBS')

    l3_net_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
    vm = test_stub.create_vm([l3_net_uuid], image_uuid, 'user_vlan_vm_s')

    test_obj_dict.add_vm(vm)
    vm.check()
    vm.stop()
    vm.reinit()
    vm.update()
    vm.check()
    vm.destroy()
    test_util.test_pass('Re-init VM Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
