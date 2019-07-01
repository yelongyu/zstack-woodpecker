# -*- coding:utf-8 -*-

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import os
import vm

vm_ops = None
iso_name = os.getenv('testIsoName')
iso_url = os.getenv('testIsoUrl')

def test():
    global vm_ops
    vm_ops = vm.VM()
    vm_ops.add_image(name=iso_name, url=iso_url)
    vm_ops.create_vm(image=iso_name, root_size='2 GB')
    vm_ops.set_boot_order(vm_ops.vm_name, cd_first=True)
    vm_ops.set_boot_order(vm_ops.vm_name, cd_first=False)
    vm_ops.check_browser_console_log()
    test_util.test_pass('Test Set Boot Order Successfully')


def env_recover():
    global vm_ops
    vm_ops.expunge_vm()
    vm_ops.expunge_image()
    vm_ops.close()

#Will be called only if exception happens in test().
def error_cleanup():
    global vm_ops
    try:
        vm_ops.expunge_vm()
        vm_ops.expunge_image()
        vm_ops.close()
    except:
        pass
