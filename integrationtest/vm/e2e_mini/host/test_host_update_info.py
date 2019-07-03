# -*- coding:utf-8 -*-
# This case will fail to pass until MINI-900 is fixed.

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import os
import host

host_ops = None
host_ip, _ = host.get_mn_ip()
host_name = 'cluster1/' + host_ip
host_new_name = 'host-rename'

def test():
    global host_ops
    global host_name
    global host_new_name
    host_ops = host.HOST()
    host_ops.update_info(res_type='host', res_name=host_name, new_name=host_new_name, new_dsc='test dsc')
    host_ops.check_browser_console_log()
    test_util.test_pass('Test Host Update Info Successful')


def env_recover():
    global host_ops
    global host_name
    global host_new_name
    host_ops.update_info(res_type='host', res_name=host_new_name, new_name=host_name, new_dsc='')
    host_ops.close()

#Will be called only if exception happens in test().
def error_cleanup():
    global host_ops
    try:
        host_ops.close()
    except:
        pass
