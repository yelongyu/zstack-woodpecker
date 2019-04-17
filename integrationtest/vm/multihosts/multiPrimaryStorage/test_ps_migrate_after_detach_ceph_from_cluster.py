'''
@author: Forat
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.primarystorage_operations as ps_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import random
import apibinding.inventory as inventory
import zstackwoodpecker.operations.datamigrate_operations as datamigr_ops

_config_ = {
        'timeout' : 3600,
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
    ps_inv = res_ops.query_resource(res_ops.PRIMARY_STORAGE)
    ceph_ps = [ps for ps in ps_inv if ps.type == 'Ceph']
    if not ceph_ps:
        test_util.test_skip('Skip test as there is not Ceph primary storage')
    
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
    if env.new_ps:
        new_ps_list.append(env.second_ps)

    test_util.test_dsc('detach Ceph Primary Storage from cluster')
    selected_ps = env.second_ps
    another_ps = env.first_ps
    ps_ops.detach_primary_storage(selected_ps.uuid, res_ops.get_resource(res_ops.CLUSTER)[0].uuid)
    detached_ps_list.append(selected_ps)

    target_vm = random.choice(first_ps_vm_list)
    target_vm.stop()
    target_vm_uuid = target_vm.get_vm().uuid
    ps_to_migrate = random.choice(datamigr_ops.get_ps_candidate_for_vm_migration(target_vm_uuid))
    ps_uuid_to_migrate = ps_to_migrate.uuid
    datamigr_ops.ps_migrage_vm(ps_uuid_to_migrate, target_vm_uuid)

    test_util.test_pass('Multi PrimaryStorage Test Pass')

def env_recover():
    for ps in detached_ps_list:
        ps_ops.attach_primary_storage(ps.uuid, res_ops.get_resource(res_ops.CLUSTER)[0].uuid)
    test_lib.lib_error_cleanup(test_obj_dict)
    if new_ps_list:
        for new_ps in new_ps_list:
            ps_ops.detach_primary_storage(new_ps.uuid, new_ps.attachedClusterUuids[0])
            ps_ops.delete_primary_storage(new_ps.uuid)
