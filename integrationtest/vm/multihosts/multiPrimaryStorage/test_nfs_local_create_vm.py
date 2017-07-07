'''
@author: FangSun
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import apibinding.inventory as inventory
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.primarystorage_operations as ps_ops

_config_ = {
        'timeout' : 3000,
        'noparallel' : True
        }

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
new_ps_list = []
VM_COUNT = 10


def try_create_vm_in_nfs(ps):
    try:
        test_util.test_dsc("Try create vm in NFS primary")
        assert ps.type == inventory.NFS_PRIMARY_STORAGE_TYPE
        test_stub.create_multi_vms(name_prefix='test-', count=VM_COUNT, ps_uuid=ps.uuid)
    except Exception as e:
        test_util.test_logger('Can not create vm in NFS, it is as expected', e)
    else:
        test_util.test_fail('Critical ERROR: can create vm in NFS ps')


def test():
    if not (test_stub.find_ps_local() and test_stub.find_ps_nfs()):
        test_util.test_skip("Skip test if not local-nfs multi ps environment")

    test_util.test_dsc("Create {0} vm ".format(VM_COUNT))
    vm_list = test_stub.create_multi_vms(name_prefix='test-', count=VM_COUNT)
    for vm in vm_list:
        test_obj_dict.add_vm(vm)

    test_util.test_dsc("Check all root volumes in LOCAL PS")
    for vm in vm_list:
        ps_uuid = vm.get_vm().allVolumes[0].primaryStorageUuid
        ps = res_ops.get_resource(res_ops.PRIMARY_STORAGE, uuid=ps_uuid)[0]
        assert ps.type == inventory.LOCAL_STORAGE_TYPE

    try_create_vm_in_nfs(test_stub.find_ps_nfs())

    test_util.test_pass('Multi PrimaryStorage Test Pass')


def env_recover():
    test_lib.lib_error_cleanup(test_obj_dict)
    if new_ps_list:
        for new_ps in new_ps_list:
            ps_ops.detach_primary_storage(new_ps.uuid, new_ps.attachedClusterUuids[0])
            ps_ops.delete_primary_storage(new_ps.uuid)