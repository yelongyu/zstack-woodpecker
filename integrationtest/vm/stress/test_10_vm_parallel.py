'''

For Stress Testing: parallel creating 10 VM. Will not destroy them.  

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
    #vm_creation_option.set_data_disk_uuids(disk_offering_uuids)
    for i in range(parallel_num):
        vm = test_stub.create_vlan_vm()
        test_obj_dict.add_vm(vm)
        #vm.destroy()
    for vm in test_obj_dict.get_vm_list():
        vm.check()

    #need regularlly clean up log files in virtual router when doing stress test
    test_lib.lib_check_cleanup_vr_logs_by_vm(test_obj_dict.get_vm_list()[0].vm)

    for vm in test_obj_dict.get_vm_list():
        vm.destroy()

    test_util.test_pass('Parallelly Create 10 VM successfully')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
