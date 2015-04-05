'''

Destroy all data volume (find from ZStack database). 

@author: Youyk
'''

import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.config_operations as con_ops
import zstackwoodpecker.operations.volume_operations as vol_ops
import zstackwoodpecker.operations.account_operations as acc_ops
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import threading
import os
import time
import apibinding.inventory as inventory

thread_threshold = os.environ.get('ZSTACK_THREAD_THRESHOLD')
if not thread_threshold:
    thread_threshold = 1000
else:
    thread_threshold = int(thread_threshold)
session_uuid = None
session_to = None
session_mc = None

def delete_volumes(volumes):
    for vl in volumes:
        thread = threading.Thread(target=vol_ops.delete_volume, args=(vl.uuid,))
        while threading.active_count() > thread_threshold:
            time.sleep(0.1)
        thread.start()

    while threading.activeCount() > 1:
        time.sleep(0.1)

def test():
    global session_to
    global session_mc
    global session_uuid
    session_to = con_ops.change_global_config('identity', 'session.timeout', '720000', session_uuid)
    session_mc = con_ops.change_global_config('identity', 'session.maxConcurrent', '10000', session_uuid)
    session_uuid = acc_ops.login_as_admin()
    cond = res_ops.gen_query_conditions('type', '=', 'Data')
    num = res_ops.query_resource_count(res_ops.VOLUME, cond, session_uuid)

    if num <= thread_threshold:
        volumes = res_ops.query_resource(res_ops.VOLUME, cond, session_uuid)
        delete_volumes(volumes)
    else:
        start = 0
        limit = thread_threshold - 1
        curr_num = start
        volumes = []
        while curr_num < num:
            volumes_temp = res_ops.query_resource_with_num(res_ops.VOLUME, cond, session_uuid, start, limit)
            volumes.extend(volumes_temp)
            start += limit
            curr_num += limit
        delete_volumes(volumes)

    #con_ops.change_global_config('identity', 'session.timeout', session_to)
    #con_ops.change_global_config('identity', 'session.maxConcurrent', session_mc)
    con_ops.change_global_config('identity', 'session.timeout', session_to, session_uuid)
    con_ops.change_global_config('identity', 'session.maxConcurrent', session_mc, session_uuid)
    left_num = res_ops.query_resource_count(res_ops.VOLUME, cond, session_uuid)
    acc_ops.logout(session_uuid)
    if left_num == 0:
        test_util.test_pass('Delete Data Volume Success. Delete %d Volumes.' % num)
    else:
        test_util.test_fail('Delete Data Volume Fail. %d Volumes are not deleted.' % left_num)

def error_cleanup():
    if session_to:
        con_ops.change_global_config('identity', 'session.timeout', session_to)
    if session_mc:
        con_ops.change_global_config('identity', 'session.maxConcurrent', session_mc)
    if session_uuid:
        acc_ops.logout(session_uuid)
