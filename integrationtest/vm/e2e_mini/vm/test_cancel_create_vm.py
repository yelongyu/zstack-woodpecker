# -*- coding:utf-8 -*-

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import vm

vm_ops = None

def test():
    global vm_ops
    vm_ops = vm.VM()
    vm_ops.cancel_create_operation(res_type='vm', close=False)
    vm_ops.cancel_create_operation(res_type='vm', close=True)
    vm_ops.check_browser_console_log()
    test_util.test_pass('Cancel VM Creation Test Successful')


def env_recover():
    global vm_ops
    vm_ops.close()

#Will be called only if exception happens in test().
def error_cleanup():
    global vm_ops
    try:
        vm_ops.close()
    except:
        pass
