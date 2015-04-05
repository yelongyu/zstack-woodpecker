'''

New Perf Test for creating snapshot operations.
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
import zstackwoodpecker.zstack_test.zstack_test_volume as test_vol_header
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
sp_name = None
exc_info = []

def create_sp(volume_uuid):
    try:
        sp_option = test_util.SnapshotOption()
        sp_option.set_name(sp_name)
        sp_option.set_volume_uuid(volume_uuid)
        sp_option.set_session_uuid(session_uuid)
        sp = vol_ops.create_snapshot(sp_option)
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
    global sp_name
    thread_threshold = os.environ.get('ZSTACK_THREAD_THRESHOLD')
    if not thread_threshold:
        thread_threshold = 1000
    else:
        thread_threshold = int(thread_threshold)
    
    sp_num = os.environ.get('ZSTACK_TEST_NUM')
    if not sp_num:
        sp_num = 0
    else:
        sp_num = int(sp_num)

    #change account session timeout. 
    session_to = con_ops.change_global_config('identity', 'session.timeout', '720000', session_uuid)
    session_mc = con_ops.change_global_config('identity', 'session.maxConcurrent', '10000', session_uuid)

    session_uuid = acc_ops.login_as_admin()
    cond = res_ops.gen_query_conditions('type', '=', 'Root')
    vol_num = res_ops.query_resource_count(res_ops.VOLUME, cond, session_uuid)
    if vol_num < thread_threshold:
        test_util.test_fail('This test needs: %d VM instances for volume attaching and detaching operations. But there are only %d VMs root volumes. Please use this case: test_crt_basic_vm_with_max_threads.py to create required VMs.' % (thread_threshold, vol_num))

    vols = res_ops.query_resource_fields(res_ops.VOLUME, cond, session_uuid, \
            ['uuid'], start = 0, limit = thread_threshold)

    test_util.test_logger('ZSTACK_THREAD_THRESHOLD is %d' % thread_threshold)
    test_util.test_logger('ZSTACK_TEST_NUM is %d' % sp_num)

    org_num = sp_num
    random_name = random.random()
    sp_name = 'perf_sp_%s' % str(random_name)
    vol_num = 0
    while sp_num > 0:
        check_thread_exception()
        sp_num -= 1
        if vol_num > (thread_threshold - 1):
            vol_num = 0
        thread = threading.Thread(target=create_sp, \
                args = (vols[vol_num].uuid, ))
        vol_num += 1
        while threading.active_count() > thread_threshold:
            time.sleep(0.1)
        thread.start()

    while threading.active_count() > 1:
        time.sleep(0.1)

    cond = res_ops.gen_query_conditions('name', '=', sp_name)
    sp_num = res_ops.query_resource_count(res_ops.VOLUME_SNAPSHOT, cond, session_uuid)
    con_ops.change_global_config('identity', 'session.timeout', session_to, session_uuid)
    con_ops.change_global_config('identity', 'session.maxConcurrent', session_mc, session_uuid)
    acc_ops.logout(session_uuid)
    if sp_num == org_num:
        test_util.test_pass('Create %d Volumes Snapshot Perf Test Success' % org_num)
    else:
        test_util.test_fail('Create %d Volumes Snapshot Perf Test Failed. Only find %d Volume Snapshots.' % (org_num, sp_num))

#Will be called only if exception happens in test().
def error_cleanup():
    if session_to:
        con_ops.change_global_config('identity', 'session.timeout', session_to, session_uuid)
    if session_mc:
        con_ops.change_global_config('identity', 'session.maxConcurrent', session_mc, session_uuid)
    if session_uuid:
        acc_ops.logout(session_uuid)
