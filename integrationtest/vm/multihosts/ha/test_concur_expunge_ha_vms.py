'''
New Integration Test for concurrent expunge vm on ceph
@author: SyZhao
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.zstack_test.zstack_test_vm as test_vm_header
import zstackwoodpecker.operations.vm_operations as vm_ops
import zstackwoodpecker.operations.ha_operations as ha_ops
import time
import os
import threading
import random

vm = None
vms  = []
ts   = []
vm_num = 20
exec_info = []
delay_policy1 = None

test_obj_dict = test_state.TestStateDict()

def create_vm_wrapper(i, vm_creation_option):
    global vms, exec_info
    try:
        vm = test_vm_header.ZstackTestVm()
        vm_creation_option.set_name("vm-%s" %(i))
        vm.set_creation_option(vm_creation_option)
        vm.create()
        ha_ops.set_vm_instance_ha_level(vm.get_vm().uuid, "NeverStop")
        vms.append(vm)
    except:
        exec_info.append("vm-%s" %(i))

def destroy_vm_wrapper(i, vm_uuid):
    global exec_info
    try:
        vm_ops.destroy_vm(vm_uuid)
    except:
        exec_info.append("vm-%s" %(i))

def expunge_vm_wrapper(i, vm_uuid):
    global vms, exec_info
    try:
        vm_ops.expunge_vm(vm_uuid)
    except:
        exec_info.append("vm-%s" %(i))

def check_exception(ops_string):
    global exec_info
    if exec_info:
        issue_vms_string = ' '.join(exec_info)
        test_util.test_fail("%s is failed to be %s." %(issue_vms_string, ops_string))

def test():
    global vms, exec_info, delete_policy1

    ps = res_ops.query_resource(res_ops.PRIMARY_STORAGE)[0]
    if ps.type != inventory.CEPH_PRIMARY_STORAGE_TYPE:
        test_util.test_skip('this test is for moniter expunge vm on ceph, not found ceph, skip test.')

    delete_policy1 = test_lib.lib_set_delete_policy('vm', 'Delay')
    image_name = os.environ.get('imageName_s')
    image_uuid = test_lib.lib_get_image_by_name(image_name).uuid
    l3_name = os.environ.get('l3NoVlanNetworkName1')
    l3_net_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid

    cpuNum = 1
    memorySize = 268435456 
    name = 'vm-offering-allocator-strategy'
    new_offering_option = test_util.InstanceOfferingOption()
    new_offering_option.set_cpuNum(cpuNum)
    new_offering_option.set_memorySize(memorySize)
    new_offering_option.set_name(name)
    new_offering = vm_ops.create_instance_offering(new_offering_option)
    test_obj_dict.add_instance_offering(new_offering)

    instance_offering_uuid = new_offering.uuid
    each_vm_cpu_consume = cpuNum 

    vm_creation_option = test_util.VmOption()
    vm_creation_option.set_l3_uuids([l3_net_uuid])
    vm_creation_option.set_image_uuid(image_uuid)
    vm_creation_option.set_instance_offering_uuid(instance_offering_uuid)


    #trigger vm create
    exec_info = []
    ts = []
    for i in range(vm_num):
        t = threading.Thread(target=create_vm_wrapper, args=(i, vm_creation_option))
        ts.append(t)
        t.start()

    for t in ts:
        t.join()

    check_exception("created")


    #trigger vm destroy
    exec_info = []
    ts = []
    for i,vm in zip(range(vm_num),vms):
        t = threading.Thread(target=destroy_vm_wrapper, args=(i, vm.vm.uuid))
        ts.append(t)
        t.start()

    for t in ts:
        t.join()

    check_exception("destroyed")


    #trigger vm expunge
    exec_info = []
    ts = []
    for i,vm in zip(range(vm_num),vms):
        t = threading.Thread(target=expunge_vm_wrapper, args=(i, vm.vm.uuid))
        ts.append(t)
        t.start()

    for t in ts:
        t.join()

    check_exception("expunged")


    test_lib.lib_set_delete_policy('vm', delete_policy1)
    test_util.test_pass('Create VM Test Success')



def error_cleanup():
    global vms
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)


def env_recover():
    global delete_policy1
    test_lib.lib_set_delete_policy('vm', delete_policy1)
    
