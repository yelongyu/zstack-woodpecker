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
VM_COUNT = 1
VOLUME_NUMBER = 10
disabled_ps_list = []


def try_create_volume_in_nfs(ps):
    try:
        test_util.test_dsc("Try create volume in NFS primary")
        assert ps.type == inventory.NFS_PRIMARY_STORAGE_TYPE
        volume = test_stub.create_multi_volume(count=1, ps=ps)[0]
    except Exception as e:
        test_util.test_logger('Can not create volume in NFS when disabled, it is as expected')
    else:
        test_obj_dict.add_volume(volume)
        test_util.test_fail('Critical ERROR: can create vm in NFS ps')


def test():

    if not (test_stub.find_ps_local() and test_stub.find_ps_nfs()):
        test_util.test_skip("Skip test if not local-nfs multi ps environment")

    nfs_ps = test_stub.find_ps_nfs()

    test_util.test_dsc("Create 1 vm  with {} data volume".format(VOLUME_NUMBER))
    vm = test_stub.create_multi_vms(name_prefix='test-', count=1, data_volume_number=VOLUME_NUMBER)
    test_obj_dict.add_vm(vm)

    test_util.test_dsc("disable NFS PS")
    ps_ops.change_primary_storage_state(nfs_ps.uuid, state='disable')
    disabled_ps_list.append(nfs_ps)

    test_util.test_dsc("make sure VM till OK and running")
    vm.check()
    assert vm.get_vm().state == 'Running'

    try_create_volume_in_nfs(nfs_ps)

    test_util.test_dsc("Try to create vm")
    new_vm = test_stub.create_multi_vms(name_prefix='test-vm', count=1)[0]
    test_obj_dict.add_vm(new_vm)

    test_util.test_pass('Multi PrimaryStorage Test Pass')


def env_recover():
    test_lib.lib_error_cleanup(test_obj_dict)
    for disabled_ps in disabled_ps_list:
        ps_ops.change_primary_storage_state(disabled_ps.uuid, state='enable')