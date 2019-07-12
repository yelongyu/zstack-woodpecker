# -*- coding:utf-8 -*-

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import os
import host

host_ops = None
host1 = None
host2 = None


def test():
    global host_ops
    global host1
    global host2
    host_ops = host.HOST()
    if os.getenv("ZSTACK_SIMULATOR") == "yes":
        host1 = 'cluster1/' + os.getenv('hostIp')
        host2 = 'cluster1/' + os.getenv('hostIp2')
    else:
        host_ip1, host_ip2 = host.get_mn_ip()
        host1 = 'cluster1/' + host_ip1
        host2 = 'cluster1/' + host_ip2
    ops_list = ['disable', 'enable', 'reconnect', 'maintenance']
    for ops in ops_list:
        host_ops.host_ops(host1, action=ops)
    for ops in ops_list:
        host_ops.host_ops(host2, action=ops, details_page=True)
    host_ops.check_browser_console_log()
    test_util.test_pass('Test Host Ops Successful')


def env_recover():
    global host_ops
    global host1
    global host2
    host_ops.host_ops([host1, host2], action='enable')
    host_ops.close()

#Will be called only if exception happens in test().
def error_cleanup():
    global host_ops
    try:
        host_ops.close()
    except:
        pass
