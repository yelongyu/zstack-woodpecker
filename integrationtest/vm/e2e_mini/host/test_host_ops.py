# -*- coding:utf-8 -*-

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import os

test_stub = test_lib.lib_get_test_stub()

mini = None
host_ip1, host_ip2 = test_stub.get_mn_ip()
host1 = 'cluster1/' + host_ip1
host2 = 'cluster1/' + host_ip2

def test():
    global mini
    mini = test_stub.MINI()
    ops_list = ['disable', 'enable', 'reconnect', 'maintenance', 'light']
    for ops in ops_list:
        mini.host_ops(host1, action=ops)
    for ops in ops_list:
        mini.host_ops(host2, action=ops, details_page=True)
    mini.check_browser_console_log()
    test_util.test_pass('Test Host Ops Successful')


def env_recover():
    global mini
    mini.close()

#Will be called only if exception happens in test().
def error_cleanup():
    global mini
    try:
        mini.close()
    except:
        pass
