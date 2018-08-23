'''

New Integration Test for cpu allocator strategy.

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
exec_info = []

test_obj_dict = test_state.TestStateDict()

def create_vm_wrapper(i, vm_creation_option):
    global invs, vms, exec_info

    try:
        vm = test_vm_header.ZstackTestVm()
        vm_creation_option.set_name("vm-%s" %(i))
        vm.set_creation_option(vm_creation_option)
        inv = vm.create()
        vms.append(vm)
    except:
        exec_info.append("vm-%s" %(i))


def check_threads_exception():
    """
    """
    global exec_info
    
    if exec_info:
        issue_vms_string = ' '.join(exec_info)
        test_util.test_fail("%s is failed to be created." %(issue_vms_string))


def prepare_host_with_different_cpu_scenario():
    """
    Prepare vms in hosts
    """
    global pre_vms
    vm_creation_option = test_util.VmOption()
    image_name = os.environ.get('imageName_s')
    image_uuid = test_lib.lib_get_image_by_name(image_name).uuid
    l3_name = os.environ.get('l3NoVlanNetworkName1')
    #l3_name = os.environ.get('l3PublicNetworkName')


    cpuNum = 6
    #cpuSpeed = 16
    memorySize = 134217728
    name = 'vm-offering-pre-cond'
    new_offering_option = test_util.InstanceOfferingOption()
    new_offering_option.set_cpuNum(cpuNum)
    #new_offering_option.set_cpuSpeed(cpuSpeed)
    new_offering_option.set_memorySize(memorySize)
    new_offering_option.set_name(name)
    new_offering = vm_ops.create_instance_offering(new_offering_option)
    test_obj_dict.add_instance_offering(new_offering)

    instance_offering_uuid = new_offering.uuid
    l3_net_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
    vm_creation_option.set_l3_uuids([l3_net_uuid])
    vm_creation_option.set_image_uuid(image_uuid)
    vm_creation_option.set_timeout(1800000)
    vm_creation_option.set_instance_offering_uuid(instance_offering_uuid)

    ps_uuid = res_ops.query_resource(res_ops.PRIMARY_STORAGE)[0].uuid
    hosts = test_lib.lib_find_hosts_by_ps_uuid(ps_uuid)
    host_id = 0
    for host, max_vm_num in zip(hosts,[3,3,3,3]):
        host_id +=1
        for i in range(max_vm_num):
            print "host_id=%s; i=%s" %(host_id, i)
            vm_creation_option.set_name('pre-create-vm-%s-%s' %(host_id, i))
            vm = test_vm_header.ZstackTestVm()
            vm_creation_option.set_host_uuid(host.uuid)
            vm.set_creation_option(vm_creation_option)
            vm.create()
            pre_vms.append(vm)
        

def get_vm_num_based_cpu_available_on_host(host_uuid, each_vm_cpu_consume):
    """
    This function is used to compute available cpu num based on host current have
    """
    host_total_cpu = test_lib.lib_get_cpu_memory_capacity(host_uuids = [host_uuid]).totalCpu
    host_avail_cpu = test_lib.lib_get_cpu_memory_capacity(host_uuids = [host_uuid]).availableCpu
    #host_total_mem = test_lib.lib_get_cpu_memory_capacity(host_uuids = [host_uuid]).totalMemory
    #host_avail_mem = test_lib.lib_get_cpu_memory_capacity(host_uuids = [host_uuid]).availableMemory

    print "total: %s; avail: %s" %(host_total_cpu, host_avail_cpu)
    return host_avail_cpu / each_vm_cpu_consume
    

def compute_total_vm_num_based_on_ps(ps_uuid, each_vm_cpu_consume):
    """
    """
    total_vm_num = 0
    hosts = test_lib.lib_find_hosts_by_ps_uuid(ps_uuid)
    for host in hosts:
        vm_num_on_host = get_vm_num_based_cpu_available_on_host(host.uuid, each_vm_cpu_consume)
        total_vm_num += vm_num_on_host
        print "@ALLOCATE: <host uuid: %s; vm num: %s>" %(host.uuid, vm_num_on_host) 

    print "@TOTAL ALLOCATE: <total vm num: %s>" %(total_vm_num)
    return total_vm_num


def clean_host_with_different_cpu_scenario():
    """
    Clean all the vms that generated from prepare function
    """
    global pre_vms
    for vm in pre_vms:
        try:
            vm.destroy()
        except:
            pass


def clean_parallel_created_vm():
    """
    """
    global vms
    for vm in vms:
        try:
            vm.destroy()
        except:
            pass

def test():
    global vms
    image_name = os.environ.get('imageName_s')
    image_uuid = test_lib.lib_get_image_by_name(image_name).uuid
    l3_name = os.environ.get('l3NoVlanNetworkName1')
    #l3_name = os.environ.get('l3PublicNetworkName')
    l3_net_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid

    cpuNum = 1
    #cpuSpeed = 16
    memorySize = 134217728
    name = 'vm-offering-allocator-strategy'
    new_offering_option = test_util.InstanceOfferingOption()
    new_offering_option.set_cpuNum(cpuNum)
    #new_offering_option.set_cpuSpeed(cpuSpeed)
    new_offering_option.set_memorySize(memorySize)
    new_offering_option.set_name(name)
    new_offering = vm_ops.create_instance_offering(new_offering_option)
    test_obj_dict.add_instance_offering(new_offering)

    #conditions = res_ops.gen_query_conditions('type', '=', 'UserVm')
    #instance_offering_inv = res_ops.query_resource(res_ops.INSTANCE_OFFERING, conditions)[0]
    #instance_offering_uuid = instance_offering_inv.uuid
    instance_offering_uuid = new_offering.uuid
    each_vm_cpu_consume = cpuNum 

    vm_creation_option = test_util.VmOption()
    vm_creation_option.set_l3_uuids([l3_net_uuid])
    vm_creation_option.set_image_uuid(image_uuid)
    vm_creation_option.set_timeout(600000)
    vm_creation_option.set_instance_offering_uuid(instance_offering_uuid)

    #create different cpu usage of hosts scenario
    prepare_host_with_different_cpu_scenario()

    #Notice here we are using the same network for both parallel vm and precondition
    #In this way, we don't need to care about the cpu cost for newly created vr.
    #If must compute vr we need to check vr existed in l3 network:
    #vrs = test_lib.lib_find_vr_by_l3_uuid(l3_1.uuid)
    ps_uuid = res_ops.query_resource(res_ops.PRIMARY_STORAGE)[0].uuid
    vm_num = compute_total_vm_num_based_on_ps(ps_uuid, each_vm_cpu_consume)

    #trigger vm create
    for i in range(vm_num):
        t = threading.Thread(target=create_vm_wrapper, args=(i, vm_creation_option))
        ts.append(t)
        t.start()

    for t in ts:
        t.join()

    check_threads_exception()

    #clean the prepare scenario
    clean_host_with_different_cpu_scenario()
    clean_parallel_created_vm()

    test_util.test_pass('Create VM Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global vms
    global pre_vms
    global test_obj_dict

    test_lib.lib_error_cleanup(test_obj_dict)
    clean_host_with_different_cpu_scenario()
    clean_parallel_created_vm()

