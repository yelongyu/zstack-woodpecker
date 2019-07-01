# -*- coding:utf-8 -*-

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import os
import vm

vm_ops = None
qga_image_name = os.getenv('testQGAImageName')
qga_image_url = os.getenv('testQGAImageUrl')

def test():
    global vm_ops
    vm_ops = vm.VM()
    vm_ops.add_image(name=qga_image_name, url=qga_image_url)
    vm_ops.create_vm(image=qga_image_name)
    vm_ops.set_qga(vm_ops.vm_name, qga=True)
    vm_ops.change_vm_password(vm_ops.vm_name)
    vm_ops.change_vm_password(vm_ops.vm_name, password='password')
    vm_ops.set_qga(vm_ops.vm_name, qga=False)
    vm_ops.check_browser_console_log()
    test_util.test_pass('Test Change VM Password Successfully')


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
