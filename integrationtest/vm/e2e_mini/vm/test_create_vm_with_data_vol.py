# -*- coding:utf-8 -*-

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import vm

vm_ops = None

def test():
    global vm_ops
    vm_ops = vm.VM()
    vm_ops.create_vm(provisioning=u'厚置备', data_size='2 GB')
    vm_ops.create_vm(provisioning=u'精简置备', data_size='2 GB', view='list')
    vm_ops.check_browser_console_log()
    test_util.test_pass('Create VM with Data Volume Successful')


def env_recover():
    global vm_ops
    vm_ops.delete_vm(corner_btn=False, del_vol=True)
    vm_ops.close()

#Will be called only if exception happens in test().
def error_cleanup():
    global vm_ops
    try:
        vm_ops.delete_vm(corner_btn=False)
        vm_ops.close()
    except:
        pass
