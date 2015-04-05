'''

Destroy all volume snapshots(find from ZStack database). 

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

thread_threshold = os.environ.get('ZSTACK_THREAD_THRESHOLD')
if not thread_threshold:
    thread_threshold = 1000
else:
    thread_threshold = int(thread_threshold)
session_uuid = None
session_to = None
session_mc = None

def delete_sps(sps):
    for sp_root in sps:
        thread = threading.Thread(target=vol_ops.delete_snapshot, \
                args=(sp_root, session_uuid))
        while threading.active_count() > thread_threshold:
            time.sleep(0.1)
        thread.start()

    while threading.activeCount() > 1:
        time.sleep(0.1)

def test():
    global session_to
    global session_mc
    global session_uuid
    session_to = con_ops.change_global_config('identity', \
            'session.timeout', '720000', session_uuid)
    session_mc = con_ops.change_global_config('identity', \
            'session.maxConcurrent', '10000', session_uuid)
    session_uuid = acc_ops.login_as_admin()
    num = res_ops.query_resource_count(res_ops.VOLUME_SNAPSHOT_TREE, [], \
            session_uuid)

    sps_del = []
    if num <= thread_threshold:
        sps = res_ops.query_resource_with_num(res_ops.VOLUME_SNAPSHOT_TREE,\
                [], session_uuid, start = 0, limit = num)
        for sp in sps:
            sps_del.append(sp.tree.inventory.uuid)
    else:
        start = 0
        limit = thread_threshold - 1
        curr_num = start
        while curr_num < num:
            sps_temp = res_ops.query_resource_with_num(\
                    res_ops.VOLUME_SNAPSHOT_TREE, \
                    [], session_uuid, start, limit)
            for sp in sps_temp:
                sps_del.append(sp.tree.inventory.uuid)
            start += limit
            curr_num += limit
    delete_sps(sps_del)

    #con_ops.change_global_config('identity', 'session.timeout', session_to)
    #con_ops.change_global_config('identity', 'session.maxConcurrent', session_mc)
    con_ops.change_global_config('identity', 'session.timeout', session_to, session_uuid)
    con_ops.change_global_config('identity', 'session.maxConcurrent', session_mc, session_uuid)
    left_num = res_ops.query_resource_count(res_ops.VOLUME_SNAPSHOT, [], \
            session_uuid)
    acc_ops.logout(session_uuid)
    if left_num == 0:
        test_util.test_pass('Delete Volume Snapshot Success. Delete %d Volume Snapshots.' % num)
    else:
        test_util.test_fail('Delete Data Volume Snapshot Fail. %d Volume Snapshots are not deleted.' % left_num)

def error_cleanup():
    if session_to:
        con_ops.change_global_config('identity', 'session.timeout', session_to)
    if session_mc:
        con_ops.change_global_config('identity', 'session.maxConcurrent', session_mc)
    if session_uuid:
        acc_ops.logout(session_uuid)
