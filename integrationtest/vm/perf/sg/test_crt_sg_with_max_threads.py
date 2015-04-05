'''

New Perf Test for creating SG and other SG rules related operations.
The created number will depends on the environment variable: ZSTACK_TEST_NUM

The default max threads are 1000. It could be modified by env variable: 
ZSTACK_THREAD_THRESHOLD

This case might need to run in KVM simulator environemnt, if there are not 
enought resource in real environment.

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

def create_sg(sg_option, l3_uuid, nic_uuid):
    try:
        #create security group
        sg = net_ops.create_security_group(sg_option)
        #add rule
        net_ops.add_rules_to_security_group(sg.uuid, rules, session_uuid)

        #attach to l3
        net_ops.attach_security_group_to_l3(sg.uuid, l3_uuid, session_uuid)

        #attach to vm
        net_ops.add_nic_to_security_group(sg.uuid, [nic_uuid], session_uuid)
    except:
        exc_info.append(sys.exc_info())

def check_thread_exception():
    if exc_info:
        info1 = exc_info[0][1]
        info2 = exc_info[0][2]
        raise info1, None, info2

def create_1k_rule():
    num = 1
    #while num < 1001:
    #while num < 101:
    while num < 11:
        rule = inventory.SecurityGroupRuleAO()
        rule.allowedCidr = '192.168.0.1/32'
        rule.endPort = 2*num + 1
        rule.startPort = 2*num
        rule.protocol = inventory.TCP
        rule.type = inventory.EGRESS
        rules.append(rule)
        num += 1

def test():
    global session_uuid
    global session_to
    global session_mc
    thread_threshold = os.environ.get('ZSTACK_THREAD_THRESHOLD')
    if not thread_threshold:
        thread_threshold = 1000
    else:
        thread_threshold = int(thread_threshold)
    
    sg_num = os.environ.get('ZSTACK_TEST_NUM')
    if not sg_num:
        sg_num = 0
    else:
        sg_num = int(sg_num)

    create_1k_rule()
    #change account session timeout. 
    session_to = con_ops.change_global_config('identity', 'session.timeout', '720000', session_uuid)
    session_mc = con_ops.change_global_config('identity', 'session.maxConcurrent', '10000', session_uuid)

    session_uuid = acc_ops.login_as_admin()

    test_util.test_logger('ZSTACK_THREAD_THRESHOLD is %d' % thread_threshold)
    test_util.test_logger('ZSTACK_TEST_NUM is %d' % sg_num)

    org_num = sg_num
    sg_option = test_util.SecurityGroupOption()
    l3_name = os.environ.get('l3VlanNetworkName1')
    conditions = res_ops.gen_query_conditions('name', '=', l3_name)
    l3_uuid = res_ops.query_resource_with_num(res_ops.L3_NETWORK, conditions, \
            session_uuid, start = 0, limit = 1)[0].uuid

    cond = res_ops.gen_query_conditions('l3NetworkUuid', '=', l3_uuid)
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
    sg_name = 'perf_sg_%s' % str(random_name)
    sg_option.set_name(sg_name)
    sg_option.set_session_uuid(session_uuid)
    vm_num = 0
    while sg_num > 0:
        check_thread_exception()
        sg_num -= 1
        sg_option.set_description(org_num - sg_num)
        if vm_num > (thread_threshold - 1):
            vm_num = 0
        thread = threading.Thread(target=create_sg, args = (sg_option, l3_uuid, nics[vm_num], ))
        vm_num += 1
        while threading.active_count() > thread_threshold:
            time.sleep(1)
        thread.start()

    while threading.active_count() > 1:
        time.sleep(0.01)

    cond = res_ops.gen_query_conditions('name', '=', sg_name)
    sgs_num = res_ops.query_resource_count(res_ops.SECURITY_GROUP, cond, session_uuid)
    con_ops.change_global_config('identity', 'session.timeout', session_to, session_uuid)
    con_ops.change_global_config('identity', 'session.maxConcurrent', session_mc, session_uuid)
    acc_ops.logout(session_uuid)
    if sgs_num == org_num:
        test_util.test_pass('Create %d SGs Test Success' % org_num)
    else:
        test_util.test_fail('Create %d SGs Test Failed. Only find %d SGs.' % (org_num, sgs_num))

#Will be called only if exception happens in test().
def error_cleanup():
    if session_to:
        con_ops.change_global_config('identity', 'session.timeout', session_to, session_uuid)
    if session_mc:
        con_ops.change_global_config('identity', 'session.maxConcurrent', session_mc, session_uuid)
    if session_uuid:
        acc_ops.logout(session_uuid)
