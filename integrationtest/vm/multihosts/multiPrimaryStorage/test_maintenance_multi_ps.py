'''
@author: FangSun
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import apibinding.inventory as inventory
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.primarystorage_operations as ps_ops
import zstackwoodpecker.operations.volume_operations as vol_ops

_config_ = {
        'timeout' : 3000,
        'noparallel' : True
        }

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
VOLUME_NUMBER = 10
maintenance_ps_list = []


def test():
    ps_list = res_ops.get_resource(res_ops.PRIMARY_STORAGE)
    if len(ps_list) < 2:
        test_util.test_skip("Skip test if only one primary storage")

    ps, another_ps = test_stub.get_ps_vm_creation()

    vm1 = test_stub.create_multi_vms(name_prefix='test-', count=1, ps_uuid=ps.uuid, data_volume_number=VOLUME_NUMBER)[0]
    vm2 = test_stub.create_multi_vms(name_prefix='test-', count=1, ps_uuid=ps.uuid)[0]

    for vm in (vm1, vm2):
        test_obj_dict.add_vm(vm)

    if another_ps.type == inventory.LOCAL_STORAGE_TYPE:
        volume_in_another = test_stub.create_multi_volume(count=VOLUME_NUMBER, ps=another_ps,
                                                          host_uuid=test_lib.lib_get_vm_host(vm2.get_vm()).uuid)
    else:
        volume_in_another = test_stub.create_multi_volume(count=VOLUME_NUMBER, ps=another_ps)

    for volume in volume_in_another:
        test_obj_dict.add_volume(volume)

    for volume in volume_in_another:
        volume.attach(vm2)

    test_util.test_dsc('set another ps in maintenance mode')
    ps_ops.change_primary_storage_state(state='maintain', primary_storage_uuid=another_ps.uuid)
    maintenance_ps_list.append(another_ps)

    vm1.update()
    vm1.check()
    vm2.update()

    assert vm1.get_vm().state == 'Running'
    assert vm2.get_vm().state == 'Stopped'

    try:
        vm2.start()
    except Exception as e:
        test_util.test_logger('Can not start vm2, it is as expected', e)
    else:
        test_util.test_fail('Critical ERROR: can start vm2 in maintenance mode')

    test_util.test_dsc('enable another ps')
    ps_ops.change_primary_storage_state(state='enable', primary_storage_uuid=another_ps.uuid)
    maintenance_ps_list.remove(another_ps)
    vm2.start()
    vm2.check()

    for volume in volume_in_another:
        volume.detach()
        volume.attach(vm2)


def env_recover():
    test_lib.lib_error_cleanup(test_obj_dict)
    for disabled_ps in maintenance_ps_list:
        ps_ops.change_primary_storage_state(disabled_ps.uuid, state='enable')