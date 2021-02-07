'''

Test for full clone vm with one data volume on local

@author: yetian
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.volume_operations as vol_ops
import zstackwoodpecker.zstack_test.zstack_test_vm as test_vm_header
import apibinding.inventory as inventory
import apibinding.api_actions as api_actions
import time
import os

vm = None
test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def test():
    global test_obj_dict, bs
    #judge whether BS is imagestore
    bs = res_ops.query_resource(res_ops.BACKUP_STORAGE)
    for i in bs:
        if i.type == inventory.IMAGE_STORE_BACKUP_STORAGE_TYPE:
	    break
    else:
        test_util.test_skip('Skip test on non-imagestore')

    #Skip for AliyunNAS PS
    ps = res_ops.query_resource(res_ops.PRIMARY_STORAGE)
    for i in ps:
        if i.type == 'AliyunNAS':
            test_util.test_skip('Skip test on AliyunNAS PS')

    image_name = os.environ.get('imageName_s')
    l3_name = os.environ.get('l3PublicNetworkName')
    vm = test_stub.create_vm("test_vm", image_name, l3_name)
    #vm.check()
    test_obj_dict.add_vm(vm)
    vm.stop()

    new_vm = vm.clone(['test_vm_clone_with_on_data_volume'], full=True)[0]
    test_obj_dict.add_vm(new_vm)

    volumes_number = len(test_lib.lib_get_all_volumes(new_vm.vm))
    if volumes_number != 1:
        test_util.test_fail('Did not find 1 volumes for [vm:] %s. But we assigned 1 data volume when create the vm. We only catch %s volumes' % (new_vm.vm.uuid, volumes_number))
    else:
        test_util.test_logger('Find 1 volumes for [vm:] %s.' % new_vm.vm.uuid)

    test_lib.lib_error_cleanup(test_obj_dict)
    test_util.test_pass('Test clone vm with one data volume Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)
