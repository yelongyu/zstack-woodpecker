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
import time

_config_ = {
        'timeout' : 3000,
        'noparallel' : True
        }

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
VOLUME_NUMBER = 10
delete_ps_list = []


def test():

    ps_list = res_ops.get_resource(res_ops.PRIMARY_STORAGE)
    if len(ps_list) < 2:
        test_util.test_skip("Skip test if only one primary storage")
    if test_stub.find_ps_local() and test_stub.find_ps_nfs():
        test_util.test_skip("Skip test for local-nfs multi ps environment")

    ps1, ps2 = test_stub.get_ps_vm_creation()

    vm1 = test_stub.create_multi_vms(name_prefix='vm1', count=1,
                                     ps_uuid=ps1.uuid, data_volume_number=VOLUME_NUMBER,
                                     ps_uuid_for_data_vol=ps1.uuid)[0]
    vm2 = test_stub.create_multi_vms(name_prefix='vm2', count=1,
                                     ps_uuid=ps1.uuid, data_volume_number=VOLUME_NUMBER,
                                     ps_uuid_for_data_vol=ps2.uuid)[0]
    vm3 = test_stub.create_multi_vms(name_prefix='vm3', count=1,
                                     ps_uuid=ps2.uuid, data_volume_number=VOLUME_NUMBER,
                                     ps_uuid_for_data_vol=ps2.uuid)[0]
    vm4 = test_stub.create_multi_vms(name_prefix='vm4', count=1,
                                     ps_uuid=ps2.uuid, data_volume_number=VOLUME_NUMBER,
                                     ps_uuid_for_data_vol=ps1.uuid)[0]
    vm_list = [vm1, vm2, vm3, vm4]

    for vm in vm_list:
        test_obj_dict.add_vm(vm)

    ps_ops.detach_primary_storage(ps2.uuid, res_ops.get_resource(res_ops.CLUSTER)[0].uuid)
    delete_ps_list.append(ps2)

    for vm in vm_list:
        vm.update()

    assert vm1.get_vm().state == 'Running'
    assert vm2.get_vm().state == 'Stopped'
    assert vm3.get_vm().state == 'Stopped'
    assert vm4.get_vm().state == 'Stopped'

    ps_ops.delete_primary_storage(ps2.uuid)
    time.sleep(10)
    conf = res_ops.gen_query_conditions('type', '=', 'UserVM')
    left_vm_list = res_ops.query_resource(res_ops.VM_INSTANCE, conf)
    assert len(left_vm_list) == 2
    left_vm_uuid_list = [vm.uuid for vm in left_vm_list]
    assert vm1.get_vm().uuid in left_vm_uuid_list
    assert vm2.get_vm().uuid in left_vm_uuid_list

    assert len(res_ops.query_resource(res_ops.VOLUME)) == \
           VOLUME_NUMBER * 2 + len(res_ops.query_resource(res_ops.VM_INSTANCE))

    test_util.test_pass('Multi PrimaryStorage Test Pass')


def env_recover():
    test_lib.lib_error_cleanup(test_obj_dict)
    for delete_ps in delete_ps_list:
        ps_config = test_util.PrimaryStorageOption()
        ps_config.set_name(delete_ps.name)
        ps_config.set_description(delete_ps.description)
        ps_config.set_zone_uuid(delete_ps.zoneUuid)
        ps_config.set_type(delete_ps.type)
        ps_config.set_url(delete_ps.url)
        if delete_ps.type == inventory.LOCAL_STORAGE_TYPE:
            new_ps = ps_ops.create_local_primary_storage(ps_config)
        elif delete_ps.type == inventory.NFS_PRIMARY_STORAGE_TYPE:
            new_ps = ps_ops.create_nfs_primary_storage(ps_config)
        else:
            new_ps = None

        ps_ops.attach_primary_storage(new_ps.uuid, res_ops.get_resource(res_ops.CLUSTER)[0].uuid)
