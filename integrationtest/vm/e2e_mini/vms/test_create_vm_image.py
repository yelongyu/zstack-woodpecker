# -*- coding:utf-8 -*-

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib

test_stub = test_lib.lib_get_test_stub()

mini = None
vm_name = 'vm-' + test_stub.get_time_postfix()
vm_image_name = 'vm_image-' + test_stub.get_time_postfix()

def test():
    global mini
    mini = test_stub.MINI()
    mini.create_vm(name=vm_name)
    mini.create_vm_image(vm_name, vm_image_name)
    mini.check_browser_console_log()
    test_util.test_pass('Test Create VM Image Successful')


def env_recover():
    global mini
    global vm_name
    global vm_image_name
    mini.delete_vm(vm_name)
    mini.delete_image(vm_image_name)
    mini.close()

#Will be called only if exception happens in test().
def error_cleanup():
    global mini
    try:
        mini.delete_vm()
        mini.close()
    except:
        pass
