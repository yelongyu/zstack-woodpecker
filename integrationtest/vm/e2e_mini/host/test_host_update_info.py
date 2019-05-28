# -*- coding:utf-8 -*-

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import os

test_stub = test_lib.lib_get_test_stub()

mini = None
host_ip, _ = test_stub.get_mn_ip()
host_name = 'cluster1/' + host_ip
host_new_name = 'host-rename'

def test():
    global mini
    global host_name
    global host_new_name
    mini = test_stub.MINI()
    mini.update_info(res_type='minihost', res_name=host_name, new_name=host_new_name, new_dsc='test dsc')
    mini.check_browser_console_log()
    test_util.test_pass('Test Host Update Info Successful')


def env_recover():
    global mini
    global host_name
    global host_new_name
    mini.update_info(res_type='minihost', res_name=host_new_name, new_name=host_name, new_dsc='')
    mini.close()

#Will be called only if exception happens in test().
def error_cleanup():
    global mini
    try:
        mini.close()
    except:
        pass
