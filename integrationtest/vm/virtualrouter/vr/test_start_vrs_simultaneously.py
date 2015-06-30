'''
Test stop all vrs, then start them simultaneously
@author: Youyk
'''

import os
import sys
import threading
import time
import zstacklib.utils.linux as linux
import apibinding.inventory as inventory
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.config_operations as con_ops
import zstackwoodpecker.operations.vm_operations as vm_ops
import zstackwoodpecker.operations.net_operations as net_ops
import zstackwoodpecker.operations.account_operations as acc_ops
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib

session_uuid = None
test_stub = test_lib.lib_get_test_stub()
exc_info = []

def start_vm(vm_uuid):
    try:
        vm_ops.start_vm(vm_uuid, session_uuid, 200000)
    except:
        exc_info.append(sys.exc_info())

def check_status(callback_data):
    vm_uuid, status = callback_data
    cond = res_ops.gen_query_conditions('state', '=', status)
    cond = res_ops.gen_query_conditions('uuid', '=', vm_uuid, cond)
    vms = res_ops.query_resource(res_ops.VM_INSTANCE, cond)
    if vms:
        return True
    return False

def check_exception():
    if exc_info:
        info1 = exc_info[0][1]
        info2 = exc_info[0][2]
        raise info1, None, info2

def stop_vm(vm_uuid):
    try:
        vm_ops.stop_vm(vm_uuid, session_uuid)
    except:
        exc_info.append(sys.exc_info())

def test():
    global session_uuid
    session_uuid = acc_ops.login_as_admin()
    l3_1_name = os.environ.get('l3VlanNetworkName1')
    l3_2_name = os.environ.get('l3VlanDNATNetworkName')
    l3_3_name = os.environ.get('l3VlanNetworkName3')
    #l3_4_name = os.environ.get('l3VlanNetworkName5')
    l3_1 = test_lib.lib_get_l3_by_name(l3_1_name)
    l3_2 = test_lib.lib_get_l3_by_name(l3_2_name)
    l3_3 = test_lib.lib_get_l3_by_name(l3_3_name)
    #l3_4 = test_lib.lib_get_l3_by_name(l3_4_name)

    #create 4 VRs.
    vrs = test_lib.lib_find_vr_by_l3_uuid(l3_1.uuid)
    if not vrs:
        vm = test_stub.create_vlan_vm(l3_name=l3_1_name)
        vm.destroy()
        vr1 = test_lib.lib_find_vr_by_l3_uuid(l3_1.uuid)[0]
    else:
        vr1 = vrs[0]

    vrs = test_lib.lib_find_vr_by_l3_uuid(l3_2.uuid)
    if not vrs:
        vm = test_stub.create_vlan_vm(l3_name=l3_2_name)
        vm.destroy()
        vr2 = test_lib.lib_find_vr_by_l3_uuid(l3_2.uuid)[0]
    else:
        vr2 = vrs[0]

    vrs = test_lib.lib_find_vr_by_l3_uuid(l3_3.uuid)
    if not vrs:
        vm = test_stub.create_vlan_vm(l3_name=l3_3_name)
        vm.destroy()
        vr3 = test_lib.lib_find_vr_by_l3_uuid(l3_3.uuid)[0]
    else:
        vr3 = vrs[0]

    #vrs = test_lib.lib_find_vr_by_l3_uuid(l3_4.uuid)
    #if not vrs:
    #    vm = test_stub.create_vlan_vm(l3_name=l3_4_name)
    #    vm.destroy()
    #    vr4 = test_lib.lib_find_vr_by_l3_uuid(l3_4.uuid)[0]
    #else:
    #    vr4 = vrs[0]

    vrs = [vr1, vr2, vr3]
    #vrs = [vr1, vr2, vr3, vr4]
    for vr in vrs:
        thread = threading.Thread(target=stop_vm, args=(vr.uuid,))
        thread.start()

    while threading.activeCount() > 1:
        check_exception()
        time.sleep(0.1)

    for vr in vrs:
        if not linux.wait_callback_success(check_status, (vr.uuid, 'Stopped'), 10):
            test_util.test_fail('VM: %s is not stopped, after waiting for extra 10s' % vr.uuid)

    check_exception()
    for vr in vrs:
        thread = threading.Thread(target=start_vm, args=(vr.uuid,))
        thread.start()

    time.sleep(1)
    acc_ops.logout(session_uuid)
    while threading.activeCount() > 1:
        check_exception()
        time.sleep(0.1)

    check_exception()
    test_util.test_pass('Test start VRs simultaneously success')

def error_cleanup():
    global session_uuid
    acc_ops.logout(session_uuid)
