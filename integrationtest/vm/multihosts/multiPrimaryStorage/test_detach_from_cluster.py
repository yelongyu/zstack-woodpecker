'''
@author: FangSun
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.primarystorage_operations as ps_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import random

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
VM_COUNT = 5
VOLUME_NUMBER = 0
new_ps_list = []
detached_ps_list = []

def test():
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

    test_util.test_dsc('detach random one Primary Storage from cluster')
    selected_ps = random.choice([env.first_ps, env.second_ps])
    if selected_ps is env.first_ps:
        another_ps = env.second_ps
    else:
        another_ps = env.first_ps
    ps_ops.detach_primary_storage(selected_ps.uuid, selected_ps.attachedClusterUuids[0])
    detached_ps_list.append(selected_ps)

    test_util.test_dsc('All vm in selected ps should STOP')
    for vm in first_ps_vm_list + second_ps_vm_list:
        vm.update()

    for vm in env.get_vm_list_from_ps(selected_ps):
        assert vm.get_vm().state == 'Stopped'

    for vm in env.get_vm_list_from_ps(another_ps):
        assert vm.get_vm().state == 'Running'

    test_util.test_dsc("Try to Create vm in detached ps")
    try:
        vm = test_stub.create_multi_vms(name_prefix='test-vm', count=1, ps_uuid=selected_ps.uuid)[0]
    except Exception as e:
        test_util.test_logger('EXPECTED: Catch exception {}\nCreate vm in disabled ps will fail'.format(e))
    else:
        test_obj_dict.add_vm(vm)
        test_util.test_fail("CRITICAL ERROR: Can create VM in ps not attached cluster")

    test_util.test_dsc("Create 5 vms and 10 Volumes and check all should be in enabled PS")
    vm_list = test_stub.create_multi_vms(name_prefix='test_vm', count=5)
    for vm in vm_list:
        test_obj_dict.add_vm(vm)
    for vm in vm_list:
        assert vm.get_vm().allVolumes[0].primaryStorageUuid == another_ps.uuid

    volume_list = test_stub.create_multi_volume(count=10)
    for volume in volume_list:
        test_obj_dict.add_volume(volume)
    for volume in volume_list:
        assert volume.get_volume().primaryStorageUuid == another_ps.uuid

    test_util.test_pass('Multi PrimaryStorage Test Pass')

def env_recover():
    for ps in detached_ps_list:
        ps_ops.attach_primary_storage(ps.uuid, res_ops.get_resource(res_ops.CLUSTER)[0])
    test_lib.lib_error_cleanup(test_obj_dict)
    if new_ps_list:
        for new_ps in new_ps_list:
            ps_ops.detach_primary_storage(new_ps.uuid, new_ps.attachedClusterUuids[0])
            ps_ops.delete_primary_storage(new_ps.uuid)
