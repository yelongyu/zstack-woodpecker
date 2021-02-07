'''
New Integration Test for creating KVM VM and check time for each stage.

@author: Glody
'''
import apibinding.inventory as inventory
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import os
import random
import string
import time

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def key_gen(key_len):
    keylist = [random.choice(string.letters+string.digits) for i in range(key_len)]
    return ("".join(keylist))

def test():
    test_util.test_dsc('Create test vm and check the time spend on each stage')

    test_util.test_skip('Time cases need further polish, skip test right now')

    vm_name = 'vm_'+key_gen(7)
    begin_time = int(time.time()*1000)
    vm = test_stub.create_named_vm(vm_name)
    test_obj_dict.add_vm(vm)
    ps = test_lib.lib_get_primary_storage_by_uuid(vm.get_vm().allVolumes[0].primaryStorageUuid)
    if ps.type != inventory.LOCAL_STORAGE_TYPE:
        test_util.test_skip('Skip test on non-localstorage')
    vr = test_lib.lib_find_vr_by_vm(vm.vm)[0]
    if vr.applianceVmType != "VirtualRouter":
        test_util.test_skip("This test only for VirtualRouter network")

    vm.check()
    [select_bs_time, allocate_host_time, allocate_ps_time, local_storage_allocate_capacity_time,\
     allocate_volume_time, allocate_nic_time, instantiate_res_pre_time, create_on_hypervisor_time,\
     instantiate_res_post_time] = test_stub.get_stage_time(vm_name, begin_time)

    test_util.test_dsc("select_bs_time is "+str(select_bs_time))
    test_util.test_dsc("allocate_host_time is "+str(allocate_host_time))
    test_util.test_dsc("allocate_ps_time is "+str(allocate_ps_time))
    test_util.test_dsc("local_storage_allocate_capacity_time is "+str(local_storage_allocate_capacity_time))
    test_util.test_dsc("allocate_volume_time is "+str(allocate_volume_time))
    test_util.test_dsc("allocate_nic_time is "+str(allocate_nic_time))
    test_util.test_dsc("instantiate_res_pre_time is "+str(instantiate_res_pre_time))
    test_util.test_dsc("create_on_hypervisor_time is "+str(create_on_hypervisor_time))
    test_util.test_dsc("instantiate_res_post_time is "+str(instantiate_res_post_time))

    if select_bs_time > 10:
        test_util.test_fail('select_bs_time is bigger than 10 milliseconds')
    if allocate_host_time > 190:
        test_util.test_fail('allocate_host_time is bigger than 190 milliseconds')
    if allocate_ps_time > 70:
        test_util.test_fail('allocate_ps_time is bigger than 70 milliseconds')
    if local_storage_allocate_capacity_time > 70:
        test_util.test_fail('local_storage_allocate_capacity_time is bigger than 70 milliseconds')
    if allocate_volume_time > 90:
        test_util.test_fail('allocate_volume_time is bigger than 90 milliseconds')
    if allocate_nic_time > 70:
        test_util.test_fail('allocate_nic_time is bigger than 70 milliseconds')
    if instantiate_res_pre_time > 1300:
        test_util.test_fail('instantiate_res_pre_time is bigger than 1300 milliseconds')
    if create_on_hypervisor_time > 2500:
        test_util.test_fail('create_on_hypervisor_time is bigger than 2500 milliseconds')
    if instantiate_res_post_time > 30:
        test_util.test_fail('instantiate_res_post_time is bigger than 30 milliseconds')

    vm.destroy()
    test_util.test_pass('Create VM and Check time for Each Stage Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
