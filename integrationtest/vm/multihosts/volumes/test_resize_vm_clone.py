'''

New Integration Test for resizing root volume.

@author: czhou25
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.volume_operations as vol_ops
import zstackwoodpecker.zstack_test.zstack_test_vm as test_vm_header
import time
import os

vm = None
test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def test():
    global vm
    vm_creation_option = test_util.VmOption()
    image_name = os.environ.get('imageName_net')
    l3_name = os.environ.get('l3VlanNetworkName1')
    vm = test_stub.create_vm("test_resize_vm", image_name, l3_name)
    test_obj_dict.add_vm(vm)
    vm.check()
    vm.stop() 
    vm.check()

    vol_size = res_ops.query_resource(res_ops.VOLUME)[0].size
    volume_uuid = res_ops.query_resource(res_ops.VOLUME)[0].uuid
    set_size = 1024*1024*1024*5
    vol_ops.resize_volume(volume_uuid, set_size)
    vol_size_after = res_ops.query_resource(res_ops.VOLUME)[0].size
    if set_size != vol_size_after:
        test_util.test_fail('Resize Root Volume failed, size = %s' % vol_size_after)

    new_vm = vm.clone(['vm_clone'])[0]
    test_obj_dict.add_vm(new_vm)
    new_volume_uuid = test_lib.lib_get_root_volume_uuid(new_vm.get_vm())
    condition = res_ops.gen_query_conditions('uuid', '=', new_volume_uuid)
    vol_size_after = res_ops.query_resource(res_ops.VOLUME, condition)[0].size
    if set_size != vol_size_after:
        test_util.test_fail('Resize Root Volume failed, size = %s' % vol_size_after) 
    test_lib.lib_error_cleanup(test_obj_dict)
    test_util.test_pass('Resize VM Snapshot Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
