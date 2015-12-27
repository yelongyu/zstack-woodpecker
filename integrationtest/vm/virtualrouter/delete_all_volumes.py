'''

Cleanup all Volumes. It is mainly for debuging.

@author: Youyk
'''

import zstackwoodpecker.operations.config_operations as con_ops
import zstackwoodpecker.operations.account_operations as acc_ops
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.clean_util as clean_util

thread_threshold=1000

session_uuid = None
session_to = None
session_mc = None

def test():
    global session_to
    global session_mc
    global session_uuid
    session_uuid = acc_ops.login_as_admin()
    session_to = con_ops.change_global_config('identity', 'session.timeout', '720000')
    session_mc = con_ops.change_global_config('identity', 'session.maxConcurrent', '10000')
    clean_util.delete_all_volumes()
    test_util.test_pass('volumes destroy Success.')
    con_ops.change_global_config('identity', 'session.timeout', session_to)
    con_ops.change_global_config('identity', 'session.maxConcurrent', session_mc)
    acc_ops.logout(session_uuid)

def error_cleanup():
    global session_uuid
    if session_to:
        con_ops.change_global_config('identity', 'session.timeout', session_to)
    if session_mc:
        con_ops.change_global_config('identity', 'session.maxConcurrent', session_mc)
    acc_ops.logout(session_uuid)
