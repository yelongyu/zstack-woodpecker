'''
@author: FangSun
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.test_state as test_state
import random
import os


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
    disk_offering_uuids = [random.choice(res_ops.get_resource(res_ops.DISK_OFFERING)).uuid]

    test_util.test_dsc("Create VM: {}".format(os.environ.get('CASE_FLAVOR')))

    vm = test_stub.create_vm_with_random_offering(vm_name='test_vm',
                                                  disk_offering_uuids=disk_offering_uuids if flavor["data_vol"] else None,
                                                  ps_uuid=local_ps.uuid if flavor["root_vol"] is LOCAL else shared_ps.uuid,
                                                  l3_name='l3VlanNetworkName1',
                                                  image_name='imageName_net',
                                                  system_tags=['primaryStorageUuidForDataVolume::{}'.format(local_ps.uuid if flavor["data_vol"] in (LOCAL, MIXED)
                                                                                                            else shared_ps.uuid)] if flavor["data_vol"] else None)

    test_obj_dict.add_vm(vm)
    vm.check()

    if flavor['data_vol'] is MIXED:
        test_util.test_dsc("Create volume from shared_ps and attached to VM")
        volume = test_stub.create_multi_volumes(count=1, ps=shared_ps)[0]
        volume.attach(vm)
        vm.check()
        test_obj_dict.add_volume(volume)

    test_util.test_dsc("Create volume in Local and attach to VM")
    local_vols = test_stub.create_multi_volumes(count=2, host_uuid=vm.get_vm().hostUuid, ps=local_ps)
    for vol in local_vols:
        test_obj_dict.add_volume(vol)
        vol.attach(vm)
        vol.check()
    vm.check()

    test_util.test_dsc("Create volume in shared and attach to VM")
    shared_vols = test_stub.create_multi_volumes(count=2, ps=shared_ps)
    for vol in shared_vols:
        test_obj_dict.add_volume(vol)
        vol.attach(vm)
        vol.check()
    vm.check()

    test_util.test_dsc("detach all volumes")
    for volume in local_vols +shared_vols:
        volume.detach()

    vm.check()

    test_lib.lib_error_cleanup(test_obj_dict)

def env_recover():
    test_lib.lib_error_cleanup(test_obj_dict)