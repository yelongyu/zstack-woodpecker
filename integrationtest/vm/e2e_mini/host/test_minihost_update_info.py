# -*- coding:utf-8 -*-

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import host

host_ops = None
minihost_name = 'cluster1'
minihost_new_name = 'cluster-rename'

def test():
    if os.getenv('ZSTACK_SIMULATOR') == "yes":
        test_util.test_skip("Simulator env don't support to enter minihost details page")
    global host_ops
    global minihost_name
    global minihost_new_name
    host_ops = host.HOST()
    host_ops.update_info(res_type='minihost', res_name=minihost_name, new_name=minihost_new_name, new_dsc='test dsc', details_page=True)
    host_ops.check_browser_console_log()
    test_util.test_pass('Test Minihost Update Info Successful')


def env_recover():
    global host_ops
    global minihost_name
    global minihost_new_name
    host_ops.update_info(res_type='minihost', res_name=minihost_new_name, new_name=minihost_name, new_dsc='', details_page=True)
    host_ops.close()

#Will be called only if exception happens in test().
def error_cleanup():
    global host_ops
    try:
        host_ops.close()
    except:
        pass
