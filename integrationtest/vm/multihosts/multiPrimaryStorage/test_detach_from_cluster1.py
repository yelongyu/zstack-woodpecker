'''
@author: FangSun
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.primarystorage_operations as ps_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import random

_config_ = {
        'timeout' : 3000,
        'noparallel' : True
        }

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
VM_COUNT = 2
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
    second_ps_vm_list = env.second_ps_vm_list
    if env.new_ps:
        new_ps_list.append(env.second_ps)

    test_util.test_dsc('detach all Primary Storage from cluster')

    for ps in [env.first_ps, env.second_ps]:
        ps_ops.detach_primary_storage(ps.uuid, ps.attachedClusterUuids[0])
        detached_ps_list.append(ps)

    test_util.test_dsc('All vm in selected ps should STOP')
    for vm in first_ps_vm_list + second_ps_vm_list:
        vm.update()

    for vm in first_ps_vm_list + second_ps_vm_list:
        assert vm.get_vm().state == 'Stopped'

    test_util.test_dsc("Try to Create one vm")
    try:
        vm = test_stub.create_multi_vms(name_prefix='test-vm', count=1)[0]
    except Exception as e:
        test_util.test_logger('EXPECTED: Catch exceptions Create vm in disabled ps will fail')
    else:
        test_obj_dict.add_vm(vm)
        test_util.test_fail("CRITICAL ERROR: Can create VM in ps not attached cluster")

    for ps in [env.first_ps, env.second_ps]:
        ps_ops.attach_primary_storage(ps.uuid, res_ops.get_resource(res_ops.CLUSTER)[0].uuid)
        detached_ps_list.remove(ps)

    for vm in first_ps_vm_list + second_ps_vm_list:
        vm.start()

    for vm in first_ps_vm_list + second_ps_vm_list:
        vm.check()
        vm.update()

    for vm in first_ps_vm_list + second_ps_vm_list:
        assert vm.get_vm().state == 'Running'

    vm = test_stub.create_multi_vms(name_prefix='test-vm', count=1)[0]
    test_obj_dict.add_vm(vm)

    test_util.test_pass('Multi PrimaryStorage Test Pass')

def env_recover():
    for ps in detached_ps_list:
        ps_ops.attach_primary_storage(ps.uuid, res_ops.get_resource(res_ops.CLUSTER)[0].uuid)
    test_lib.lib_error_cleanup(test_obj_dict)
    if new_ps_list:
        for new_ps in new_ps_list:
            ps_ops.detach_primary_storage(new_ps.uuid, new_ps.attachedClusterUuids[0])
            ps_ops.delete_primary_storage(new_ps.uuid)
