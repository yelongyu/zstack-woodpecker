'''
Test stop vrs then start it
@author: Quarkonics
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
import zstackwoodpecker.operations.ha_operations as ha_ops
import zstackwoodpecker.operations.account_operations as acc_ops
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib

_config_ = {
        'timeout' : 1000,
        'noparallel' : True
        }

session_uuid = None
test_stub = test_lib.lib_get_test_stub()

def test():
    global session_uuid
    session_uuid = acc_ops.login_as_admin()
    l3_1_name = os.environ.get('l3VlanNetworkName1')
    l3_1 = test_lib.lib_get_l3_by_name(l3_1_name)

    #create VRs.
    vrs = test_lib.lib_find_vr_by_l3_uuid(l3_1.uuid)
    if not vrs:
        vm = test_stub.create_vlan_vm(l3_name=l3_1_name)
        vm.destroy()
        vr1 = test_lib.lib_find_vr_by_l3_uuid(l3_1.uuid)[0]
    else:
        vr1 = vrs[0]

    vm_ops.stop_vm(vr1.uuid)
    if test_lib.lib_get_ha_enable() != 'true':
        vm_ops.start_vm(vr1.uuid)

    vr1_mgmt_ip = test_lib.lib_find_vr_mgmt_ip(vr1)
    if not test_lib.lib_wait_target_up(vr1_mgmt_ip, '7272', 120):
        test_util.test_fail('vr: %s is not startup in 120 seconds. Fail to reboot it. ' % vr1.uuid)

    timeout = time.time() + 60
    while time.time() < timeout:
        cond = res_ops.gen_query_conditions('uuid', '=', vr1.uuid) 
        vms = res_ops.query_resource(res_ops.VM_INSTANCE, cond)
        if vms[0].status == 'Connected':
            test_util.test_pass('Test Reconnect VR VM start VRs success')
        time.sleep(1)

    test_util.test_fail('VR VM: %s is not connected within 60 seconds' % vr1.uuid)

def error_cleanup():
    global session_uuid
    acc_ops.logout(session_uuid)
