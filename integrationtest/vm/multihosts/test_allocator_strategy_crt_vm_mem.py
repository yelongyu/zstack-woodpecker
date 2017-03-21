'''

New Integration Test for mem allocator strategy.

@author: SyZhao
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.zstack_test.zstack_test_vm as test_vm_header
import zstackwoodpecker.operations.vm_operations as vm_ops
import time
import os
import threading
import random

vm = None
pre_vms = []
vms  = []
ts   = []
invs = []
vm_num = 9

test_obj_dict = test_state.TestStateDict()

def create_vm_wrapper(i, vm_creation_option):
    global invs, vms

    vm = test_vm_header.ZstackTestVm()
    vm_creation_option.set_name("vm-%s" %(i))
    vm.set_creation_option(vm_creation_option)

    inv = vm.create()
    vms.append(vm)
    #if inv:
    #    invs.append(inv)


def prepare_host_with_different_mem_scenario():
    """
    Prepare vms in hosts
    """
    global pre_vms

    vm_creation_option = test_util.VmOption()
    image_name = os.environ.get('imageName_s')
    image_uuid = test_lib.lib_get_image_by_name(image_name).uuid
    #l3_name = os.environ.get('l3NoVlanNetworkName1')
    l3_name = os.environ.get('l3PublicNetworkName')


    l3_net_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
    conditions = res_ops.gen_query_conditions('type', '=', 'UserVm')
    instance_offering_uuid = res_ops.query_resource(res_ops.INSTANCE_OFFERING, conditions)[0].uuid
    #instance_offering_uuid = new_offering.uuid
    vm_creation_option.set_l3_uuids([l3_net_uuid])
    vm_creation_option.set_image_uuid(image_uuid)
    vm_creation_option.set_instance_offering_uuid(instance_offering_uuid)

    ps_uuid = res_ops.query_resource(res_ops.PRIMARY_STORAGE)[0].uuid
    hosts = test_lib.lib_find_hosts_by_ps_uuid(ps_uuid)
    for host in hosts:
        max_vm_num = random.randint(1, 3)
        for i in range(max_vm_num):
            vm_creation_option.set_name('pre-create-vm%s' %(i))
            vm = test_vm_header.ZstackTestVm()
            vm_creation_option.set_host_uuid(host.uuid)
            vm.set_creation_option(vm_creation_option)
            pre_vms.append(vm.create())
        

def get_vm_num_based_mem_available_on_host(host_uuid, each_vm_mem_consume):
    """
    This function is used to compute available mem num based on host current have
    """
    #host_total_cpu = test_lib.lib_get_cpu_memory_capacity(host_uuids = [host_uuid]).totalCpu
    #host_avail_cpu = test_lib.lib_get_cpu_memory_capacity(host_uuids = [host_uuid]).availableCpu
    host_total_mem = test_lib.lib_get_cpu_memory_capacity(host_uuids = [host_uuid]).totalMemory
    host_avail_mem = test_lib.lib_get_cpu_memory_capacity(host_uuids = [host_uuid]).availableMemory

    return host_avail_mem / each_vm_mem_consume
    

def compute_total_vm_num_based_on_ps(ps_uuid, each_vm_mem_consume):
    """
    """
    total_vm_num = 0
    hosts = test_lib.lib_find_hosts_by_ps_uuid(ps_uuid)
    for host in hosts:
        total_vm_num += get_vm_num_based_mem_available_on_host(host.uuid, each_vm_mem_consume)

    return total_vm_num


def clean_host_with_different_mem_scenario():
    """
    Clean all the vms that generated from prepare function
    """
    global pre_vms

    for vm in pre_vms:
        vm.destory()
        vm.expunge()


def test():
    global vms
    image_name = os.environ.get('imageName_s')
    image_uuid = test_lib.lib_get_image_by_name(image_name).uuid
    #l3_name = os.environ.get('l3NoVlanNetworkName1')
    l3_name = os.environ.get('l3PublicNetworkName')
    l3_net_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid

    cpuNum = 1
    cpuSpeed = 8
    memorySize = 536870912
    name = 'vm-offering-allocator-strategy'
    new_offering_option = test_util.InstanceOfferingOption()
    new_offering_option.set_cpuNum(cpuNum)
    new_offering_option.set_cpuSpeed(cpuSpeed)
    new_offering_option.set_memorySize(memorySize)
    new_offering_option.set_name(name)
    new_offering = vm_ops.create_instance_offering(new_offering_option)
    test_obj_dict.add_instance_offering(new_offering)

    #conditions = res_ops.gen_query_conditions('type', '=', 'UserVm')
    #instance_offering_inv = res_ops.query_resource(res_ops.INSTANCE_OFFERING, conditions)[0]
    #instance_offering_uuid = instance_offering_inv.uuid
    instance_offering_uuid = new_offering.uuid
    each_vm_mem_consume = memorySize

    vm_creation_option = test_util.VmOption()
    vm_creation_option.set_l3_uuids([l3_net_uuid])
    vm_creation_option.set_image_uuid(image_uuid)
    vm_creation_option.set_instance_offering_uuid(instance_offering_uuid)

    #create different mem usage of hosts scenario
    prepare_host_with_different_mem_scenario()

    ps_uuid = res_ops.query_resource(res_ops.PRIMARY_STORAGE)[0].uuid
    vm_num = compute_total_vm_num_based_on_ps(ps_uuid, each_vm_mem_consume)
    #trigger vm create
    for i in range(vm_num):
        t = threading.Thread(target=create_vm_wrapper, args=(i, vm_creation_option))
        ts.append(t)
        t.start()

    for t in ts:
        t.join()

    for vm in vms:
        if not test_lib.lib_check_login_in_vm(vm.get_vm(), 'root', 'password'):
            test_util.test_fail("batch creating vm is failed")


    #clean the prepare scenario
    clean_host_with_different_mem_scenario()

    test_util.test_pass('Create VM Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global vms
    global pre_vms
    global test_obj_dict

    test_lib.lib_error_cleanup(test_obj_dict)
    clean_host_with_different_mem_scenario()

    for vm in vms:
        try:
            vm.destroy()
            vm.expunge()
        except:
            pass

    for vm in pre_vms:
        try:
            vm.destroy()
            vm.expunge()
        except:
            pass
