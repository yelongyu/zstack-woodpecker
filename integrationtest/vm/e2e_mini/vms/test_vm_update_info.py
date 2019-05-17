# -*- coding:utf-8 -*-

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib

test_stub = test_lib.lib_get_test_stub()

mini = None
vm_name = 'test-vm'
vm_new_name='vm-rename'

def test():
    global mini
    global vm_name
    global vm_new_name
    mini = test_stub.MINI()
    mini.create_vm(name=vm_name)
    mini.update_info(res_type='vm', res_name=vm_name, new_name=vm_new_name, new_dsc='test dsc')
    mini.check_browser_console_log()
    test_util.test_pass('Test VM Update Info Successful')


def env_recover():
    global mini
    global vm_new_name
    mini.delete_vm(vm_new_name)
    mini.close()

#Will be called only if exception happens in test().
def error_cleanup():
    global mini
    try:
        mini.delete_vm()
        mini.close()
    except:
        pass
