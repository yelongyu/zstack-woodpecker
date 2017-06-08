'''
@author: FangSun
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.primarystorage_operations as ps_ops


test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
new_ps_list = []
VM_COUNT = 10

def test():
    test_util.test_dsc("Create {0} volume in the first primaryStorage".format(VM_COUNT))
    ps_list = res_ops.get_resource(res_ops.PRIMARY_STORAGE)
    first_ps = ps_list[0]
    volume_list = test_stub.create_multi_volume(count=VM_COUNT, ps=first_ps)
    for volume in volume_list:
        test_obj_dict.add_volume(volume)

    if len(ps_list) == 1:
        test_util.test_dsc("Add Another primaryStorage")
        second_ps = test_stub.add_primaryStorage(first_ps=first_ps)
        new_ps_list.append(second_ps)
    else:
        second_ps = ps_list[1]

    test_util.test_dsc("Create {0} volume in the second primaryStorage".format(VM_COUNT))
    volume_list = test_stub.create_multi_volume(count=VM_COUNT, ps=second_ps)
    for volume in volume_list:
        test_obj_dict.add_volume(volume)

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