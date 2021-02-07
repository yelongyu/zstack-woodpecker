'''
@author: FangSun
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.primarystorage_operations as ps_ops
import apibinding.inventory as inventory
import random

_config_ = {
        'timeout' : 7200,
        'noparallel' : True
        }

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
new_ps_list = []
VOLUME_NUMBER = 100



def test():
    test_util.test_dsc("Create {0} volume in the first primaryStorage".format(VOLUME_NUMBER))
    ps_env = test_stub.PSEnvChecker()
    ps_list = res_ops.get_resource(res_ops.PRIMARY_STORAGE)
    if ps_env.is_sb_ceph_env:
        first_ps = random.choice([ps for ps in ps_list if ps.type == inventory.CEPH_PRIMARY_STORAGE_TYPE])
    else:
        first_ps = random.choice(ps_list)
    volume_list = test_stub.create_multi_volumes(count=VOLUME_NUMBER, ps=first_ps)
    for volume in volume_list:
        test_obj_dict.add_volume(volume)

    if len(ps_list) == 1:
        test_util.test_dsc("Add Another primaryStorage")
        second_ps = test_stub.add_primaryStorage(first_ps=first_ps)
        new_ps_list.append(second_ps)
    else:
        second_ps = random.choice([ps for ps in ps_list if ps.uuid != first_ps.uuid])

    test_util.test_dsc("Create {0} volume in the second primaryStorage".format(VOLUME_NUMBER))
    volume_list = test_stub.create_multi_volumes(count=VOLUME_NUMBER, ps=second_ps)
    for volume in volume_list:
        test_obj_dict.add_volume(volume)

    test_util.test_dsc("Create one more volume in the first primaryStorage")
    volume = test_stub.create_multi_volumes(count=1, ps=first_ps)[0]
    test_obj_dict.add_volume(volume)

    test_util.test_dsc("Check the capacity")
    #To do

    test_util.test_pass('Multi PrimaryStorage Test Pass')


def env_recover():
    test_util.test_dsc("Destroy test object")
    test_lib.lib_error_cleanup(test_obj_dict)
    if new_ps_list:
        for new_ps in new_ps_list:
            ps_ops.detach_primary_storage(new_ps.uuid, new_ps.attachedClusterUuids[0])
            ps_ops.delete_primary_storage(new_ps.uuid)