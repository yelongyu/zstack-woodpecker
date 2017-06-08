'''
@author: FangSun
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.volume_operations as vol_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import apibinding.inventory as inventory
import apibinding.api_actions as api_actions
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.header.host as host_header
import os
import zstackwoodpecker.operations.primarystorage_operations as ps_ops
import random


test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
new_ps_list = []
VM_COUNT = 2

def test():
    test_util.test_dsc("Create {0} vm in the first primaryStorage".format(VM_COUNT))
    ps_list = res_ops.get_resource(res_ops.PRIMARY_STORAGE)
    first_ps = ps_list[0]
    vm_list = test_stub.create_multi_vms(name_prefix='vm_in_fist_ps', count=VM_COUNT, ps_uuid=first_ps.uuid)
    for vm in vm_list:
        test_obj_dict.add_vm(vm)

    if len(ps_list) == 1:
        test_util.test_dsc("Add Another primaryStorage")
        second_ps = test_stub.add_primaryStorage(first_ps=first_ps)
        new_ps_list.append(second_ps)
    else:
        second_ps = ps_list[1]

    test_util.test_dsc("Create {0} vm in the second primaryStorage".format(VM_COUNT))
    vm_list = test_stub.create_multi_vms(name_prefix='vm_in_second_ps', count=VM_COUNT, ps_uuid=second_ps.uuid)
    for vm in vm_list:
        test_obj_dict.add_vm(vm)

    test_util.test_dsc("Check the capacity")
    #To do

    test_util.test_dsc("Destroy test object")
    test_lib.lib_error_cleanup(test_obj_dict)

    if new_ps_list:
        test_util.test_dsc("Remove new added primaryStorage")
        for new_ps in new_ps_list:
            ps_ops.detach_primary_storage(new_ps.uuid, new_ps.attachedClusterUuids[0])
            ps_ops.delete_primary_storage(new_ps.uuid)

    test_util.test_pass('Multi PrimaryStorage Test Pass')


#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
    if new_ps_list:
        for new_ps in new_ps_list:
            ps_ops.detach_primary_storage(new_ps.uuid, new_ps.attachedClusterUuids[0])
            ps_ops.delete_primary_storage(new_ps.uuid)

