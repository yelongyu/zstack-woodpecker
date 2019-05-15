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
    mini.vm_ops(vm_name, action='stop')
    mini.vm_ops(vm_name, action='start')
    mini.vm_ops(vm_name, action='reboot')
    mini.vm_ops(vm_name, action='stop', details_page=True)
    mini.vm_ops(vm_name, action='start', details_page=True)
    mini.vm_ops(vm_name, action='reboot', details_page=True)
    mini.check_browser_console_log()
    test_util.test_pass('Start, Stop and Reboot VM Successful')


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
