'''

Destroy all security groups (find from ZStack database). 

@author: Youyk
'''

import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.config_operations as con_ops
import zstackwoodpecker.operations.net_operations as net_ops
import zstackwoodpecker.operations.account_operations as acc_ops
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import apibinding.inventory as inventory
import threading
import os
import time
import sys

thread_threshold = os.environ.get('ZSTACK_THREAD_THRESHOLD')
if not thread_threshold:
    thread_threshold = 1000
else:
    thread_threshold = int(thread_threshold)
session_uuid = None
session_to = None
session_mc = None

def delete_sgs(sgs):
    for sg in sgs:
        thread = threading.Thread(target=net_ops.delete_security_group, args=(sg.uuid, session_uuid))
        while threading.active_count() > thread_threshold:
            time.sleep(0.05)
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
    session_to = con_ops.change_global_config('identity', 'session.timeout', '720000', session_uuid)
    session_mc = con_ops.change_global_config('identity', 'session.maxConcurrent', '10000', session_uuid)
    session_uuid = acc_ops.login_as_admin()
    num = res_ops.query_resource_count(res_ops.SECURITY_GROUP, [], session_uuid)

    if num <= thread_threshold:
        sgs = res_ops.query_resource(res_ops.SECURITY_GROUP, [], session_uuid)
        delete_sgs(sgs)
    else:
        start = 0
        limit = thread_threshold - 1
        curr_num = start
        sgs = []
        while curr_num < num:
            sgs_tmp = res_ops.query_resource_fields(res_ops.SECURITY_GROUP, \
                    [], session_uuid, ['uuid'], start, limit)
            sgs.extend(sgs_tmp)
            curr_num += limit
            start += limit
        delete_sgs(sgs)

    #con_ops.change_global_config('identity', 'session.timeout', session_to)
    #con_ops.change_global_config('identity', 'session.maxConcurrent', session_mc)
    con_ops.change_global_config('identity', 'session.timeout', session_to, session_uuid)
    con_ops.change_global_config('identity', 'session.maxConcurrent', session_mc, session_uuid)
    left_num = res_ops.query_resource_count(res_ops.SECURITY_GROUP, [], session_uuid)
    acc_ops.logout(session_uuid)
    if left_num == 0:
        test_util.test_pass('Delete SG Success. Delete %d SGs.' % num)
    else:
        test_util.test_fail('Delete SG Fail. %d SGs are not deleted.' % left_num)

def error_cleanup():
    if session_to:
        con_ops.change_global_config('identity', 'session.timeout', session_to)
    if session_mc:
        con_ops.change_global_config('identity', 'session.maxConcurrent', session_mc)
    if session_uuid:
        acc_ops.logout(session_uuid)
