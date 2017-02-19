'''

New Perf Test for creating KHost Host with basic L3 network.
The created number will depend on the environment variable: ZSTACK_TEST_NUM

The difference with test_basic_l3_host_with_given_num.py is this case's max thread is 1000 

@author: Youyk
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.host_operations as host_ops
import zstackwoodpecker.operations.config_operations as con_ops
import zstackwoodpecker.operations.account_operations as acc_ops
import os
import time 
import threading
import random
import sys

session_uuid = None
session_to = None
session_mc = None
get_all_host_ip = []
thread_threshold = os.environ.get('ZSTACK_THREAD_THRESHOLD')

if not thread_threshold:
    thread_threshold = 100
else:
    thread_threshold = int(thread_threshold)

start_IP = os.environ.get('MultiHostStartIP')
end_IP = os.environ.get('MultiHostEndIP')
hostname = os.environ.get('MultiHostUsername')
password = os.environ.get('MultiHostPassword')

if not start_IP or not end_IP or not hostname or not password:
    test_util.test_fail("Fail to get host info for multi adding!")
else:
    test_util.test_logger('Start IP is %s' % start_IP)
    test_util.test_logger('End IP is %s' % end_IP)
    test_util.test_logger('Hostname is %s' % hostname)
    test_util.test_logger('Password is %s' % password)

cluster = res_ops.get_resource(res_ops.CLUSTER)
if not cluster:
    test_util.test_fail("No cluster avaiable!")

exc_info = []
def check_thread_exception():
    if exc_info:
        info1 = exc_info[0][1]
        info2 = exc_info[0][2]
        raise info1, None, info2


def add_host_by_ip(host_ip):
    host_config = test_util.HostOption()
    host_config.set_name(host_ip)
    host_config.set_cluster_uuid(cluster[0].uuid)
    host_config.set_management_ip(host_ip)
    host_config.set_username(hostname)
    host_config.set_password(password)
    try:
        host_ops.add_kvm_host(host_config)
    except:
        exc_info.append(sys.exc_info())

def test():
    global session_uuid
    global session_to
    global session_mc
    global get_all_host_ip 
    session_to = con_ops.change_global_config('identity', 'session.timeout', '720000', session_uuid)
    session_mc = con_ops.change_global_config('identity', 'session.maxConcurrent', '10000', session_uuid)
    session_uuid = acc_ops.login_as_admin()
    get_all_host_ip = test_lib.get_ip(start_IP, end_IP)
    host_num = len(get_all_host_ip)
    i = 0
    tmp_host_num = host_num
    while tmp_host_num > 0:
        check_thread_exception()
        tmp_host_num -= 1
        thread = threading.Thread(target=add_host_by_ip, args=(get_all_host_ip[i],))
        i += 1
        while threading.active_count() > thread_threshold:
            time.sleep(1)
        thread.start()
    while threading.active_count() > 1:
        time.sleep(0.01)


def check_operation_result():
    for i in get_all_host_ip:
        v1 = test_lib.lib_get_host_by_ip(i)
        if not v1:
            test_util.test_fail('Fail to Add Host %s.' % v1.uuid)

#Will be called only if exception happens in test().
def error_cleanup():
    if session_to:
        con_ops.change_global_config('identity', 'session.timeout', session_to, session_uuid)
    if session_mc:
        con_ops.change_global_config('identity', 'session.maxConcurrent', session_mc, session_uuid)
    if session_uuid:
        acc_ops.logout(session_uuid)
