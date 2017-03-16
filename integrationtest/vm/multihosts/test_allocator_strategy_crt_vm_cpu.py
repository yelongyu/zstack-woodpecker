'''

New Integration Test for creating KVM VM.

@author: Youyk
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.zstack_test.zstack_test_vm as test_vm_header
import time
import os
import threading

vm = None
vms  = []
ts   = []
invs = []
vm_num = 9

def create_vm_wrapper(vm_obj):
    global invs, vms

    inv = vm_obj.create()
    vms.append(vm_obj)
    if inv:
        invs.append(inv)


def prepare_host_with_different_cpu_scenario():
    """
    Prepare 1 vm already in host1
    Prepare 2 vms already in host2
    Prepare 2 vms already in host3
    """
    pass


def clean_host_with_different_cpu_scenario()
    """
    Clean all the vms that generated from prepare function
    """
    pass



def test():
    global vm
    vm_creation_option = test_util.VmOption()
    image_name = os.environ.get('imageName_s')
    image_uuid = test_lib.lib_get_image_by_name(image_name).uuid
    #l3_name = os.environ.get('l3NoVlanNetworkName1')
    l3_name = os.environ.get('l3VlanNetworkName1')

    l3_net_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
    conditions = res_ops.gen_query_conditions('type', '=', 'UserVm')
    instance_offering_uuid = res_ops.query_resource(res_ops.INSTANCE_OFFERING, conditions)[0].uuid
    vm_creation_option.set_l3_uuids([l3_net_uuid])
    vm_creation_option.set_image_uuid(image_uuid)
    vm_creation_option.set_instance_offering_uuid(instance_offering_uuid)
    vm_creation_option.set_name('multihost_basic_vm')
    vm = test_vm_header.ZstackTestVm()
    vm.set_creation_option(vm_creation_option)

    #create different cpu usage of hosts scenario
    prepare_host_with_different_cpu_scenario()


    #trigger vm create
    for i in range(vm_num):
        t = threading.Thread(target=create_vm_wrapper, args=(vm))
        ts.append(t)
        t.start()

    for t in ts:
        t.join()

    for vm_inv in invs:
        if not test_lib.lib_check_login_in_vm(vm_inv.get_vm(), 'root', 'password'):
            test_util.test_fail("batch creating vm is failed")

    for vm in vms:
        vm.destroy()
        vm.expunge()
        vm.check()


    #clean the prepare scenario
    clean_host_with_different_cpu_scenario()

    test_util.test_pass('Create VM Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global vms
    clean_host_with_different_cpu_scenario()
    for vm in vms:
        try:
            vm.destroy()
        except:
            pass
