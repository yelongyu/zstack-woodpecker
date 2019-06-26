'''
MINI VMs concurrent operations test
VM num: 7
VM InstanceOffering: 8C 16GB

1.create
2.stop
3.start
4.expunge
'''

import apibinding.inventory as inventory
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
vms  = []
ts   = []
vm_num = 7
exec_info = []

test_obj_dict = test_state.TestStateDict()

def create_vm_wrapper(i, vm_creation_option):
    global vms, exec_info
    try:
        vm = test_vm_header.ZstackTestVm()
        vm_creation_option.set_name("vm-%s" %(i))
        vm.set_creation_option(vm_creation_option)
        vm.create()
        vms.append(vm)
    except:
        exec_info.append("vm-%s" %(i))

def stop_vm_wrapper(i, vm_uuid):
    global exec_info
    try:
        vm_ops.stop_vm(vm_uuid)
    except:
        exec_info.append("vm-%s" %(i))

def start_vm_wrapper(i, vm_uuid):
    global exec_info
    try:
        vm_ops.start_vm(vm_uuid)
    except:
        exec_info.append("vm-%s" % (i))

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
    global vms, exec_info 

    VM_CPU= 8
    VM_MEM = 17179869184 #16GB 

    vm_creation_option = test_util.VmOption()
    image_name = os.environ.get('imageName_s')
    image_uuid = test_lib.lib_get_image_by_name(image_name).uuid
    l3_name = os.environ.get('l3VlanNetworkName1')
    l3_net_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid

    vm_creation_option.set_l3_uuids([l3_net_uuid])
    vm_creation_option.set_image_uuid(image_uuid)
    vm_creation_option.set_cpu_num(VM_CPU)
    vm_creation_option.set_memory_size(VM_MEM)
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

    #trigger vm stop
    exec_info = []
    ts = []
    for i,vm in zip(range(vm_num),vms):
        t = threading.Thread(target=stop_vm_wrapper, args=(i, vm.vm.uuid))
        ts.append(t)
        t.start()
    for t in ts:
        t.join()

    check_exception("stopped")

    #trigger vm start
    exec_info = []
    ts = []
    for i,vm in zip(range(vm_num),vms):
        t = threading.Thread(target=start_vm_wrapper, args=(i, vm.vm.uuid))
        ts.append(t)
        t.start()
    for t in ts:
        t.join()

    check_exception("started")

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


    test_util.test_pass('Create VM Test Success')



def error_cleanup():
    global vms
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)


def env_recover():
    global delete_policy1
    pass 
