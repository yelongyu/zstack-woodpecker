'''

New Perf Test for creating vip and pf.
The created number will depends on the environment variable: ZSTACK_TEST_NUM

The default max threads are 1000. It could be modified by env variable: 
ZSTACK_THREAD_THRESHOLD

@author: Youyk
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.config_operations as con_ops
import zstackwoodpecker.operations.account_operations as acc_ops
import zstackwoodpecker.operations.volume_operations as vol_ops
import zstackwoodpecker.operations.net_operations as net_ops
import zstackwoodpecker.zstack_test.zstack_test_volume as test_vol_header
import apibinding.inventory as inventory

import time
import os
import sys
import threading
import random

_config_ = {
    'timeout' : 10000,
    'noparallel' : True 
}

session_uuid = None
session_to = None
session_mc = None
exc_info = []
rules = []

def create_pf(vip_option, nic_uuid, num):
    try:
        #create vip and eip
        vip = net_ops.create_vip(vip_option)
        pf_option = test_util.PortForwardingRuleOption()
        if num < 32767:
            port_s = 2 * num
            port_e = port_s + 1
            pf_option.set_allowedCidr('192.168.0.1/32')
        else:
            port_s = num / 20
            port_e = port_s + 1
            pf_option.set_allowedCidr('192.168.%d.%d/32' % (num / 1000, num % 255))

        pf_option.set_vip_uuid(vip.uuid)
        pf_option.set_vm_nic_uuid(nic_uuid)
        pf_option.set_session_uuid(session_uuid)
        pf_option.set_protocol(inventory.TCP)
        pf_option.set_private_ports(port_s, port_e)
        pf_option.set_vip_ports(port_s, port_e)
        pf_option.set_name('pf_%s' % vip_option.get_name())

        pf = net_ops.create_port_forwarding(pf_option)
    except:
        exc_info.append(sys.exc_info())

def check_thread_exception():
    if exc_info:
        info1 = exc_info[0][1]
        info2 = exc_info[0][2]
        raise info1, None, info2

def test():
    global session_uuid
    global session_to
    global session_mc
    thread_threshold = os.environ.get('ZSTACK_THREAD_THRESHOLD')
    if not thread_threshold:
        thread_threshold = 1000
    else:
        thread_threshold = int(thread_threshold)
    
    vip_num = os.environ.get('ZSTACK_TEST_NUM')
    if not vip_num:
        vip_num = 0
    else:
        vip_num = int(vip_num)

    #change account session timeout. 
    session_to = con_ops.change_global_config('identity', 'session.timeout', '720000', session_uuid)
    session_mc = con_ops.change_global_config('identity', 'session.maxConcurrent', '10000', session_uuid)

    session_uuid = acc_ops.login_as_admin()

    test_util.test_logger('ZSTACK_THREAD_THRESHOLD is %d' % thread_threshold)
    test_util.test_logger('ZSTACK_TEST_NUM is %d' % vip_num)

    org_num = vip_num
    vip_option = test_util.VipOption()
    l3_name = os.environ.get('l3PublicNetworkName')
    conditions = res_ops.gen_query_conditions('name', '=', l3_name)
    l3_uuid = res_ops.query_resource_with_num(res_ops.L3_NETWORK, conditions, \
            session_uuid, start = 0, limit = 1)[0].uuid

    cond = res_ops.gen_query_conditions('l3NetworkUuid', '!=', l3_uuid)
    vm_nic_num = res_ops.query_resource_count(res_ops.VM_NIC, cond, \
            session_uuid)

    if vm_nic_num < thread_threshold:
        test_util.test_fail('This test needs: %d vm nics for pf attaching and detaching operations. But there are only %d vm nics. Please use this case: test_crt_basic_vm_with_max_threads.py to create required VMs.' % (thread_threshold, vm_nic_num))

    vm_nics = res_ops.query_resource_fields(res_ops.VM_NIC, cond, \
            session_uuid, ['uuid'], 0, thread_threshold)

    nics = []
    for nic in vm_nics:
        nics.append(nic.uuid)
    random_name = random.random()
    vip_name = 'perf_vip_%s' % str(random_name)
    vip_option.set_name(vip_name)
    vip_option.set_session_uuid(session_uuid)
    vip_option.set_l3_uuid(l3_uuid)
    vm_num = 0
    while vip_num > 0:
        check_thread_exception()
        vip_num -= 1
        vip_option.set_description(org_num - vip_num)
        if vm_num > (thread_threshold - 1):
            vm_num = 0
        thread = threading.Thread(target=create_pf, args = (vip_option, nics[vm_num], (vm_num + 1)))
        vm_num += 1
        while threading.active_count() > thread_threshold:
            time.sleep(1)
        thread.start()

    while threading.active_count() > 1:
        time.sleep(0.01)

    cond = res_ops.gen_query_conditions('name', '=', 'pf_%s' % vip_name)
    pf_num = res_ops.query_resource_count(res_ops.PORT_FORWARDING, cond, \
            session_uuid)
    con_ops.change_global_config('identity', 'session.timeout', session_to, \
            session_uuid)
    con_ops.change_global_config('identity', 'session.maxConcurrent', \
            session_mc, session_uuid)
    acc_ops.logout(session_uuid)
    if pf_num == org_num:
        test_util.test_pass('Create %d PFs Test Success' % org_num)
    else:
        test_util.test_fail('Create %d PFs Test Failed. Only find %d PFs.' % (org_num, pf_num))

#Will be called only if exception happens in test().
def error_cleanup():
    if session_to:
        con_ops.change_global_config('identity', 'session.timeout', session_to, session_uuid)
    if session_mc:
        con_ops.change_global_config('identity', 'session.maxConcurrent', session_mc, session_uuid)
    if session_uuid:
        acc_ops.logout(session_uuid)
