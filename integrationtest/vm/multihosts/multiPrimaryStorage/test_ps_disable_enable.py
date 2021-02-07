'''
@author: FangSun
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.primarystorage_operations as ps_ops
import random

_config_ = {
        'timeout' : 3000,
        'noparallel' : True
        }

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
VM_COUNT = 1
VOLUME_NUMBER = 0
new_ps_list = []
disabled_ps_list = []
LOOP = 5


@test_stub.skip_if_local_shared
def test():
    ps_env = test_stub.PSEnvChecker()
    if ps_env.is_sb_ceph_env:
        env = test_stub.SanAndCephPrimaryStorageEnv(test_object_dict=test_obj_dict,
                                             first_ps_vm_number=VM_COUNT,
                                             second_ps_vm_number=VM_COUNT,
                                             first_ps_volume_number=VOLUME_NUMBER,
                                             second_ps_volume_number=VOLUME_NUMBER)
    else:
        env = test_stub.TwoPrimaryStorageEnv(test_object_dict=test_obj_dict,
                                             first_ps_vm_number=VM_COUNT,
                                             second_ps_vm_number=VM_COUNT,
                                             first_ps_volume_number=VOLUME_NUMBER,
                                             second_ps_volume_number=VOLUME_NUMBER)
    env.check_env()
    env.deploy_env()
    first_ps_vm_list = env.first_ps_vm_list
    first_ps_volume_list = env.first_ps_volume_list
    second_ps_vm_list = env.second_ps_vm_list
    second_ps_volume_list = env.second_ps_volume_list
    if env.new_ps:
        new_ps_list.append(env.second_ps)
    tbj_list = first_ps_vm_list + second_ps_vm_list + first_ps_volume_list + second_ps_volume_list

    for _ in xrange(LOOP):
        test_util.test_dsc('Disable random one Primary Storage')
        disabled_ps = random.choice([env.first_ps, env.second_ps])
        if disabled_ps is env.first_ps:
            enabled_ps = env.second_ps
        else:
            enabled_ps = env.first_ps
        ps_ops.change_primary_storage_state(disabled_ps.uuid, state='disable')
        disabled_ps_list.append(disabled_ps)

        test_util.test_dsc('make sure all VM and Volumes still OK and running')
        for test_object in tbj_list:
            test_object.check()

        test_util.test_dsc("Try to Create vm in disabeld ps")
        with test_stub.expected_failure("Create vm in disabled ps", Exception):
            test_stub.create_multi_vms(name_prefix='test-vm', count=1, ps_uuid=disabled_ps.uuid)

        test_util.test_dsc("Create 2 vms and check all should be in enabled PS")
        if ps_env.is_sb_ceph_env:
            if disabled_ps.uuid == env.first_ps:
                vm_list = test_stub.create_multi_vms(name_prefix='test_vm', count=2, ps_uuid=enabled_ps.uuid, bs_type="Ceph")
            else:
                vm_list = test_stub.create_multi_vms(name_prefix='test_vm', count=2, ps_uuid=enabled_ps.uuid, bs_type="ImageStoreBackupStorage")
        else:
            vm_list = test_stub.create_multi_vms(name_prefix='test_vm', count=2)
        for vm in vm_list:
            test_obj_dict.add_vm(vm)
        for vm in vm_list:
            assert vm.get_vm().allVolumes[0].primaryStorageUuid != disabled_ps.uuid

        ps_ops.change_primary_storage_state(disabled_ps.uuid, state='enable')
        disabled_ps_list.pop()
    test_util.test_pass('Multi PrimaryStorage Test Pass')


def env_recover():
    test_lib.lib_error_cleanup(test_obj_dict)
    for disabled_ps in disabled_ps_list:
        ps_ops.change_primary_storage_state(disabled_ps.uuid, state='enable')
    if new_ps_list:
        for new_ps in new_ps_list:
            ps_ops.detach_primary_storage(new_ps.uuid, new_ps.attachedClusterUuids[0])
            ps_ops.delete_primary_storage(new_ps.uuid)
