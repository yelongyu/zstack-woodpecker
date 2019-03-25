'''
@author: FangSun
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.primarystorage_operations as ps_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import random
import apibinding.inventory as inventory

_config_ = {
        'timeout' : 3000,
        'noparallel' : True
        }


test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
VM_COUNT = 1
VOLUME_NUMBER = 0
new_ps_list = []
detached_ps_list = []


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
    second_ps_vm_list = env.second_ps_vm_list
    if env.new_ps:
        new_ps_list.append(env.second_ps)

    test_util.test_dsc('detach random one Primary Storage from cluster')
    selected_ps = random.choice([env.first_ps, env.second_ps])
    if selected_ps is env.first_ps:
        another_ps = env.second_ps
    else:
        another_ps = env.first_ps
    ps_ops.detach_primary_storage(selected_ps.uuid, res_ops.get_resource(res_ops.CLUSTER)[0].uuid)
    detached_ps_list.append(selected_ps)

    test_util.test_dsc('All vm in selected ps should STOP')
    for vm in first_ps_vm_list + second_ps_vm_list:
        vm.update()

    for vm in env.get_vm_list_from_ps(selected_ps):
        assert vm.get_vm().state == inventory.STOPPED

    for vm in env.get_vm_list_from_ps(another_ps):
        assert vm.get_vm().state == inventory.RUNNING

    with test_stub.expected_failure('start vm in ps that not attached to cluster', Exception):
        random.choice(env.get_vm_list_from_ps(selected_ps)).start()

    with test_stub.expected_failure("Create vm in detached ps", Exception):
        test_stub.create_multi_vms(name_prefix='test-vm', count=1, ps_uuid=selected_ps.uuid)

    test_util.test_dsc("Create 5 vms and check all should be in enabled PS")
    if ps_env.is_sb_ceph_env:
        if selected_ps.type == "SharedBlock":
            vm_list = test_stub.create_multi_vms(name_prefix='test_vm', count=5, bs_type='Ceph')
        else:
            vm_list = test_stub.create_multi_vms(name_prefix='test_vm', count=5, bs_type='ImageStoreBackupStorage')
    else:
        vm_list = test_stub.create_multi_vms(name_prefix='test_vm', count=5)
    for vm in vm_list:
        test_obj_dict.add_vm(vm)
    for vm in vm_list:
        assert vm.get_vm().allVolumes[0].primaryStorageUuid == another_ps.uuid

    test_util.test_pass('Multi PrimaryStorage Test Pass')

def env_recover():
    for ps in detached_ps_list:
        ps_ops.attach_primary_storage(ps.uuid, res_ops.get_resource(res_ops.CLUSTER)[0].uuid)
    test_lib.lib_error_cleanup(test_obj_dict)
    if new_ps_list:
        for new_ps in new_ps_list:
            ps_ops.detach_primary_storage(new_ps.uuid, new_ps.attachedClusterUuids[0])
            ps_ops.delete_primary_storage(new_ps.uuid)
