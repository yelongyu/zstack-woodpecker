'''
@author: FangSun
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import apibinding.inventory as inventory
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.primarystorage_operations as ps_ops
import time

_config_ = {
        'timeout' : 3000,
        'noparallel' : True
        }

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
VOLUME_NUMBER = 10
delete_ps_list = []


@test_stub.skip_if_local_shared
@test_stub.skip_if_only_one_ps
def test():
    ps_env = test_stub.PSEnvChecker()

    ps1, ps2 = ps_env.get_two_ps()

    for _ in xrange(5):
        test_util.test_dsc('Remove ps2')
        ps_ops.detach_primary_storage(ps2.uuid, res_ops.get_resource(res_ops.CLUSTER)[0].uuid)
        ps_ops.delete_primary_storage(ps2.uuid)
        delete_ps_list.append(ps2)
        test_util.test_dsc('Add ps2 back')
        ps_config = test_util.PrimaryStorageOption()
        ps_config.set_name(ps2.name)
        ps_config.set_description(ps2.description)
        ps_config.set_zone_uuid(ps2.zoneUuid)
        ps_config.set_type(ps2.type)
        ps_config.set_url(ps2.url)
        if ps2.type == inventory.LOCAL_STORAGE_TYPE:
            ps2 = ps_ops.create_local_primary_storage(ps_config)
        elif ps2.type == inventory.NFS_PRIMARY_STORAGE_TYPE:
            ps2 = ps_ops.create_nfs_primary_storage(ps_config)
        else:
            ps2 = None
        time.sleep(5)
        ps_ops.attach_primary_storage(ps2.uuid, res_ops.get_resource(res_ops.CLUSTER)[0].uuid)
        time.sleep(5)
        delete_ps_list.pop()

    test_util.test_dsc('create VM by default para')
    vm1 = test_stub.create_multi_vms(name_prefix='vm1', count=1, data_volume_number=VOLUME_NUMBER)[0]
    test_obj_dict.add_vm(vm1)

    if ps_env.is_local_nfs_env:
        test_util.test_dsc('create date volume in ps2')
        volume = test_stub.create_multi_volumes(count=VOLUME_NUMBER, ps=ps2)
        test_obj_dict.add_volume(volume)
    else:
        test_util.test_dsc('create VM in ps2')
        vm2 = test_stub.create_multi_vms(name_prefix='vm2', count=1, ps_uuid=ps2.uuid,
                                        data_volume_number=VOLUME_NUMBER)[0]
        test_obj_dict.add_vm(vm2)

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
