'''

For POC Testing: keep creating/destroying vm in 24hr

@author: Youyk
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import os
import time
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.zstack_test.zstack_test_vm as zstack_vm_header

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

duration = 24*60*60

def test():
    image_name = os.environ.get('imageName_net')
    image_uuid = test_lib.lib_get_image_by_name(image_name).uuid
    l3_name = os.environ.get('l3VlanNetworkName1')

    l3_net_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
    l3_uuid_list = [l3_net_uuid]
    vm_creation_option = test_util.VmOption()
    conditions = res_ops.gen_query_conditions('type', '=', 'UserVm')
    instance_offering_uuid = res_ops.query_resource(res_ops.INSTANCE_OFFERING, conditions)[0].uuid
    times = 1
    vm_name = '24hr_vm-'
    vm_creation_option.set_instance_offering_uuid(instance_offering_uuid)
    vm_creation_option.set_l3_uuids(l3_uuid_list)
    vm_creation_option.set_image_uuid(image_uuid)
    #vm_creation_option.set_data_disk_uuids(disk_offering_uuids)
    current_time = time.time()
    end_time = current_time + duration
    while current_time < end_time:
        times = times + 1
        vm_creation_option.set_name(vm_name + str(times))
        vm = zstack_vm_header.ZstackTestVm()
        vm.set_creation_option(vm_creation_option)
        vm.create()
        time.sleep(5)
        vm.destroy()
    test_util.test_pass('Keep create/destroy %s VMs in 24 hrs pass' % times)

#Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)
