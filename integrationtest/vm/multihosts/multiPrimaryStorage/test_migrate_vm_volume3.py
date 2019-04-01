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
VOLUME_NUMBER = 10
new_ps_list = []


@test_stub.skip_if_have_local
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

    first_ps_vm = random.choice(env.first_ps_vm_list)
    first_ps_volume_list = env.first_ps_volume_list
    second_ps_vm = random.choice(env.second_ps_vm_list)
    second_ps_volume_list = env.second_ps_volume_list
    if env.new_ps:
        new_ps_list.append(env.second_ps)

    test_util.test_dsc("Attach volume to VM in first Primary Storage")
    for volume in first_ps_volume_list + second_ps_volume_list:
        volume.attach(first_ps_vm)

    for volume in first_ps_volume_list + second_ps_volume_list:
        volume.check()

    test_stub.migrate_vm_to_random_host(first_ps_vm)
    first_ps_vm.check()

    for volume in first_ps_volume_list + second_ps_volume_list:
        volume.check()
        assert volume.get_volume().vmInstanceUuid == first_ps_vm.get_vm().uuid

    for volume in first_ps_volume_list + second_ps_volume_list:
        volume.detach()

    for volume in first_ps_volume_list + second_ps_volume_list:
        volume.check()


    test_util.test_dsc("Attach volume to vm in second Primary Storage")
    for volume in first_ps_volume_list + second_ps_volume_list:
        volume.attach(second_ps_vm)

    for volume in first_ps_volume_list + second_ps_volume_list:
        volume.check()

    test_stub.migrate_vm_to_random_host(second_ps_vm)
    second_ps_vm.check()

    for volume in first_ps_volume_list + second_ps_volume_list:
        volume.check()
        assert volume.get_volume().vmInstanceUuid == second_ps_vm.get_vm().uuid

    test_util.test_pass('Multi PrimaryStorage Test Pass')



def env_recover():
    test_lib.lib_error_cleanup(test_obj_dict)
    if new_ps_list:
        for new_ps in new_ps_list:
            ps_ops.detach_primary_storage(new_ps.uuid, new_ps.attachedClusterUuids[0])
            ps_ops.delete_primary_storage(new_ps.uuid)
