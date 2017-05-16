'''

@author: Quarkonics
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.volume_operations as vol_ops

_config_ = {
        'timeout' : 1000,
        'noparallel' : True
        }

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def test():
    global test_obj_dict
    cond = res_ops.gen_query_conditions('state', '=', 'Enabled')
    cond = res_ops.gen_query_conditions('type', '=', 'LocalStorage', cond)
    cond = res_ops.gen_query_conditions('status', '=', 'Connected', cond)
    ps = res_ops.query_resource(res_ops.PRIMARY_STORAGE, cond)
    if len(ps) < 2:
        test_util.test_skip("Requres at least two local ps")

    ps1_res = vol_ops.get_local_storage_capacity(None, ps[0].uuid)[0]
    ps2_res = vol_ops.get_local_storage_capacity(None, ps[1].uuid)[0]

    if ps1_res.availableCapacity > ps2_res.availableCapacity:
        data_volume_size = ps2_res.availableCapacity + (ps1_res.availableCapacity - ps2_res.availableCapacity) / 2
    else:
        data_volume_size = ps1_res.availableCapacity + (ps2_res.availableCapacity - ps1_res.availableCapacity) / 2
    disk_offering_option = test_util.DiskOfferingOption()
    disk_offering_option.set_name('2-local-ps-test')
    disk_offering_option.set_diskSize(data_volume_size)
    data_volume_offering = vol_ops.create_volume_offering(disk_offering_option)
    test_obj_dict.add_disk_offering(data_volume_offering)
    vm = test_stub.create_vlan_vm(disk_offering_uuids=[data_volume_offering.uuid])
    test_obj_dict.add_vm(vm)

    test_lib.lib_robot_cleanup(test_obj_dict)
    test_util.test_pass('2 Local PS Test Pass')
    return False

def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)
