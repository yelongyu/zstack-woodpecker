# -*- coding:utf-8 -*-

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import os
import vm

vm_ops = None
image_ops = None
iso_name = os.getenv('testIsoName')
iso_url = os.getenv('testIsoUrl')

def test():
    global vm_ops
    global image_ops
    vm_ops = vm.VM()
    image = test_lib.lib_get_specific_stub(suite_name='e2e_mini/image', specific_name='image')
    image_ops = image.IMAGE(uri=vm_ops.uri, initialized=True)
    image_ops.add_image(name=iso_name, url=iso_url)
    vm_ops.create_vm(image=iso_name, root_size='2 GB')
    vm_ops.check_browser_console_log()
    test_util.test_pass('Create VM with ISO Image Successfully')


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
