'''

Cleanup all VMs  (find from ZStack database). It is mainly for debuging.

@author: Youyk
'''
import threading
import time
import sys

import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.config_operations as con_ops
import zstackwoodpecker.operations.net_operations as net_ops
import zstackwoodpecker.operations.vm_operations as vm_ops
import zstackwoodpecker.operations.account_operations as acc_ops
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import apibinding.inventory as inventory

thread_threshold=1000
session_uuid = None
session_to = None
session_mc = None

def destroy_vips(vips):
    for vip in vips:
        thread = threading.Thread(target=net_ops.delete_vip, args=(vip.uuid,))
        while threading.active_count() > thread_threshold:
            time.sleep(0.5)
        exc = sys.exc_info()
        if exc[0]:
            raise info1, None, info2
        thread.start()

    while threading.activeCount() > 1:
        exc = sys.exc_info()
        if exc[0]:
            raise info1, None, info2
        time.sleep(0.1)

def destroy_vms(vms):
    for vm in vms:
        thread = threading.Thread(target=vm_ops.destroy_vm, args=(vm.uuid,))
        while threading.active_count() > thread_threshold:
            time.sleep(0.5)
        exc = sys.exc_info()
        if exc[0]:
            raise info1, None, info2
        thread.start()

    while threading.activeCount() > 1:
        exc = sys.exc_info()
        if exc[0]:
            raise info1, None, info2
        time.sleep(0.1)

def test():
    global session_to
    global session_mc
    global session_uuid
    session_uuid = acc_ops.login_as_admin()
    session_to = con_ops.change_global_config('identity', 'session.timeout', '720000', session_uuid)
    session_mc = con_ops.change_global_config('identity', 'session.maxConcurrent', '10000', session_uuid)
    cond = res_ops.gen_query_conditions('type', '=', inventory.USER_VM_TYPE)
    num = res_ops.query_resource_count(res_ops.VM_INSTANCE, cond, session_uuid)

    if num <= thread_threshold:
        vms = res_ops.query_resource(res_ops.VM_INSTANCE, cond, session_uuid)
        destroy_vms(vms)
    else:
        start = 0
        limit = thread_threshold - 1
        curr_num = start
        vms = []
        while curr_num < num:
            vms_temp = res_ops.query_resource_fields(res_ops.VM_INSTANCE, \
                    cond, session_uuid, ['uuid'], start, limit)
            vms.extend(vms_temp)
            curr_num += limit
            start += limit
        destroy_vms(vms)

    vip_num = res_ops.query_resource_count(res_ops.VIP, [], session_uuid)

    if vip_num <= thread_threshold:
        vips = res_ops.query_resource(res_ops.VIP, [], session_uuid)
        destroy_vips(vips)
    else:
        start = 0
        limit = thread_threshold - 1
        curr_num = start
        vms = []
        while curr_num < vip_num:
            vips_temp = res_ops.query_resource_fields(res_ops.VIP, \
                    [], session_uuid, ['uuid'], start, limit)
            vips.extend(vips_temp)
            curr_num += limit
            start += limit
        destroy_vips(vips)
    #con_ops.change_global_config('identity', 'session.timeout', session_to)
    #con_ops.change_global_config('identity', 'session.maxConcurrent', session_mc)
    left_num = res_ops.query_resource_count(res_ops.VM_INSTANCE, cond, session_uuid)
    if left_num == 0:
        test_util.test_pass('None VR VMs destroy Success. Destroy %d VMs.' % num)
    else:
        test_util.test_fail('None VR VMs destroy Fail. %d VMs are not Destroied.' % left_num)

    left_num = res_ops.query_resource_count(res_ops.VIP, [], session_uuid)
    if left_num == 0:
        test_util.test_pass('VIP destroy Success. Destroy %d VIP.' % num)
    else:
        test_util.test_fail('VIP destroy Fail. %d VIP are not Destroied.' % left_num)

    con_ops.change_global_config('identity', 'session.timeout', session_to, session_uuid)
    con_ops.change_global_config('identity', 'session.maxConcurrent', session_mc, session_uuid)
    acc_ops.logout(session_uuid)

def error_cleanup():
    if session_to:
        con_ops.change_global_config('identity', 'session.timeout', session_to)
    if session_mc:
        con_ops.change_global_config('identity', 'session.maxConcurrent', session_mc)
    if session_uuid:
        acc_ops.logout(session_uuid)
