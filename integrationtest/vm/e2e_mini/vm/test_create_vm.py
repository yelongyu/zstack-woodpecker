# -*- coding:utf-8 -*-

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import vm

vm_ops = None

def test():
    global vm_ops
    vm_ops = vm.VM()
    vm_ops.create_vm(provisioning=u'厚置备', view='list')
    vm_ops.create_vm(provisioning=u'精简置备')
    vm_ops.check_browser_console_log()
    test_util.test_pass('Create VM Successful')


def env_recover():
    global vm_ops
    vm_ops.expunge_vm()
    vm_ops.close()

#Will be called only if exception happens in test().
def error_cleanup():
    global vm_ops
    try:
        vm_ops.expunge_vm()
        vm_ops.close()
    except:
        pass
