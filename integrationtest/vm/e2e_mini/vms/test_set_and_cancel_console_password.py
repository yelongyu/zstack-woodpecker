# -*- coding:utf-8 -*-

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib

test_stub = test_lib.lib_get_test_stub()

mini = None
vm_name = 'vm-' + test_stub.get_time_postfix()

def test():
    global mini
    mini = test_stub.MINI()
    mini.create_vm(name=vm_name)
    for details_page in [False, True]:
        mini.set_console_password(vm_name, details_page=details_page, end_action='cancel')
        mini.set_console_password(vm_name, details_page=details_page, end_action='close')
        mini.set_console_password(vm_name, details_page=details_page)
        mini.cancel_console_password(vm_name, details_page=details_page, end_action='cancel')
        mini.cancel_console_password(vm_name, details_page=details_page, end_action='close')
        mini.cancel_console_password(vm_name, details_page=details_page)
    mini.check_browser_console_log()
    test_util.test_pass('Set and Cancel the Console  Password of VM Successful')


def env_recover():
    global mini
    mini.expunge_vm(vm_name)
    mini.close()

#Will be called only if exception happens in test().
def error_cleanup():
    global mini
    try:
        mini.expunge_vm(vm_name)
        mini.close()
    except:
        pass
