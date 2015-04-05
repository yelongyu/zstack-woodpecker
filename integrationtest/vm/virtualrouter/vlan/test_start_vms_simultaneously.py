'''
Test stop 4 vms, then start them simultaneously
@author: Youyk
'''

import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.config_operations as con_ops
import zstackwoodpecker.operations.vm_operations as vm_ops
import zstackwoodpecker.operations.net_operations as net_ops
import zstackwoodpecker.operations.account_operations as acc_ops
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import threading
import time
import apibinding.inventory as inventory
import sys
import os

session_uuid = None
test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def test():
    global session_uuid
    session_uuid = acc_ops.login_as_admin()
    l3_name = os.environ.get('l3VlanDNATNetworkName')
    vm1 = test_stub.create_vlan_vm(l3_name=l3_name)
    test_obj_dict.add_vm(vm1)
    vm2 = test_stub.create_vlan_vm(l3_name=l3_name)
    test_obj_dict.add_vm(vm2)
    vm3 = test_stub.create_vlan_vm(l3_name=l3_name)
    test_obj_dict.add_vm(vm3)
    vm4 = test_stub.create_vlan_vm(l3_name=l3_name)
    test_obj_dict.add_vm(vm4)

    vms = [vm1, vm2, vm3, vm4]

    for vm in vms:
        thread = threading.Thread(target=vm_ops.stop_vm, args=(vm.get_vm().uuid, session_uuid,))
        thread.start()

    while threading.activeCount() > 1:
        time.sleep(0.1)

    for vm in vms:
        thread = threading.Thread(target=vm_ops.start_vm, args=(vm.get_vm().uuid, session_uuid,))
        thread.start()

    vm1.check()
    vm2.check()
    vm3.check()
    vm4.check()

    time.sleep(1)
    acc_ops.logout(session_uuid)
    while threading.activeCount() > 1:
        time.sleep(0.1)
    test_lib.lib_robot_cleanup(test_obj_dict)
    test_util.test_pass('Test start VRs simultaneously success')

def error_cleanup():
    global session_uuid
    acc_ops.logout(session_uuid)
    test_lib.lib_error_cleanup(test_obj_dict)
