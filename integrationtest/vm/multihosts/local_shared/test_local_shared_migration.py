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

    test_util.test_dsc("Try to perform live migration")
    if flavor['root_vol'] is SHARED and flavor['data_vol'] in (None, SHARED):
        test_stub.migrate_vm_to_random_host(vm)
    elif flavor['root_vol'] is LOCAL and flavor['data_vol'] is None:
        test_util.test_dsc("Try to perform local vm live migration")
        test_stub.migrate_vm_to_random_host(vm)
    else:
        with test_lib.expected_failure("live migration will fail if have local volumes", Exception):
            test_stub.migrate_vm_to_random_host(vm)
    vm.check()

    test_util.test_dsc("Try to perform cold migration")
    if local_vol:
        local_vol.detach()
    if shared_vol:
        shared_vol.detach()
    vm.stop()
    vm.check()

    if flavor['root_vol'] is LOCAL:
        target_host = test_lib.lib_find_random_host(vm.get_vm())
        vol_ops.migrate_volume(test_lib.lib_get_root_volume(vm.get_vm()).uuid, target_host.uuid)
        if local_vol:
            vol_ops.migrate_volume(local_vol.get_volume().uuid, target_host.uuid)
        if shared_vol:
            with test_lib.expected_failure('cold migrate volume in shared ps', Exception):
                vol_ops.migrate_volume(shared_vol.get_volume().uuid, target_host.uuid)

    if local_vol:
        local_vol.attach(vm)
    if shared_vol:
        shared_vol.attach(vm)
    vm.start()
    vm.check()

    test_util.test_dsc("Try to perform detached VM hot migration")
    if flavor['root_vol'] is SHARED and flavor['data_vol'] in (LOCAL, MIXED):
        if local_vol:
            local_vol.detach()
        if shared_vol:
            shared_vol.detach()

        test_stub.migrate_vm_to_random_host(vm)

        if local_vol:
            vol_ops.migrate_volume(local_vol.get_volume().uuid, vm.get_vm().hostUuid)

        if local_vol:
            local_vol.attach(vm)
        if shared_vol:
            shared_vol.attach(vm)
        vm.check()

    test_lib.lib_error_cleanup(test_obj_dict)
    test_util.test_pass('Multi PrimaryStorage Test Pass')


def env_recover():
    test_lib.lib_error_cleanup(test_obj_dict)
