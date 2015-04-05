'''

For POC Testing: parallel creating 10 VM. 

@author: Youyk
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import os
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.zstack_test.zstack_test_vm as zstack_vm_header

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

parallel_num = 10

def test():
    image_name = os.environ.get('imageName_net')
    image_uuid = test_lib.lib_get_image_by_name(image_name).uuid
    l3_name = os.environ.get('l3VlanNetworkName1')

    l3_net_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
    l3_uuid_list = [l3_net_uuid]
    vm_creation_option = test_util.VmOption()
    conditions = res_ops.gen_query_conditions('type', '=', 'UserVm')
    instance_offering_uuid = res_ops.query_resource(res_ops.INSTANCE_OFFERING, conditions)[0].uuid
    vm_name = 'parallel_vm-'
    vm_creation_option.set_instance_offering_uuid(instance_offering_uuid)
    vm_creation_option.set_l3_uuids(l3_uuid_list)
    vm_creation_option.set_image_uuid(image_uuid)
    #vm_creation_option.set_data_disk_uuids(disk_offering_uuids)
    for i in range(parallel_num):
        i = i + 1
        vm_creation_option.set_name(vm_name + str(i))
        vm = zstack_vm_header.ZstackTestVm()
        vm.set_creation_option(vm_creation_option)
        vm.create()
        test_obj_dict.add_vm(vm)
 
    #vm.destroy()
    test_util.test_pass('Parallelly Create 10 VM successfully')

#Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)
