'''
@author: FangSun
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.test_state as test_state
import random
import os
import zstackwoodpecker.operations.volume_operations as vol_ops

_config_ = {
        'timeout' : 3000,
        'noparallel' : True
        }

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()


SHARED='SHARED'
LOCAL='LOCAL'
MIXED='MIXED'

case_flavor = dict(root_local=             dict(root_vol=LOCAL, data_vol=None),
                   root_local_data_local=  dict(root_vol=LOCAL, data_vol=LOCAL),
                   root_local_data_shared= dict(root_vol=LOCAL, data_vol=SHARED),
                   root_local_data_mixed=  dict(root_vol=LOCAL, data_vol=MIXED),
                   root_shared=            dict(root_vol=SHARED, data_vol=None),
                   root_shared_data_local= dict(root_vol=SHARED, data_vol=LOCAL),
                   root_shared_data_shared=dict(root_vol=SHARED, data_vol=SHARED),
                   root_shared_data_mixed= dict(root_vol=SHARED, data_vol=MIXED),
                   )


@test_stub.skip_if_not_local_shared
def test():
    flavor = case_flavor[os.environ.get('CASE_FLAVOR')]
    ps_env = test_stub.PSEnvChecker()
    local_ps, shared_ps = ps_env.get_two_ps()

    test_util.test_dsc("Create VM: {}".format(os.environ.get('CASE_FLAVOR')))

    vm = test_stub.create_vm_with_random_offering(vm_name='test_vm',
                                                  ps_uuid=local_ps.uuid if flavor["root_vol"] is LOCAL else shared_ps.uuid,
                                                  l3_name='l3VlanNetworkName1',
                                                  image_name='imageName_net')

    test_obj_dict.add_vm(vm)

    if flavor['data_vol'] in (LOCAL, MIXED):
        local_vol = test_stub.create_multi_volumes(count=1,host_uuid=vm.get_vm().hostUuid, ps=local_ps)[0]
        test_obj_dict.add_volume(local_vol)
        local_vol.attach(vm)
    else:
        local_vol = None

    if flavor['data_vol'] in (SHARED, MIXED):
        shared_vol = test_stub.create_multi_volumes(count=1, ps=shared_ps)[0]
        test_obj_dict.add_volume(shared_vol)
        shared_vol.attach(vm)
    else:
        shared_vol = None

    vm.check()
    vm.update()

    snapshots_list = []
    for volume in vm.get_vm().allVolumes:
        snapshots = test_obj_dict.get_volume_snapshot(volume.uuid)
        snapshots.set_utility_vm(vm)
        snapshots.create_snapshot('create_volume_snapshot')
        snapshots_list.append(snapshots)

    vm.stop()
    vm.check()

    for snapshots in snapshots_list:
        snapshot = snapshots.get_current_snapshot()
        snapshots.use_snapshot(snapshot)

    vm.start()
    vm.check()

    if local_vol:
        local_vol.detach()
    if shared_vol:
        shared_vol.detach()

    vm.check()

    test_lib.lib_error_cleanup(test_obj_dict)
    test_util.test_pass('Multi PrimaryStorage Test Pass')


def env_recover():
    test_lib.lib_error_cleanup(test_obj_dict)
