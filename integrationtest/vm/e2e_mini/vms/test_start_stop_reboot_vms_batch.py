# -*- coding:utf-8 -*-

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib

test_stub = test_lib.lib_get_test_stub()

mini = None
vm_name_list = ['vm-' + test_stub.get_time_postfix() for _ in range(3)]

def test():
    global mini
    mini = test_stub.MINI()
    for vm_name in vm_name_list:
        mini.create_vm(name=vm_name)
    mini.vm_ops(vm_name_list, action='stop')
    mini.vm_ops(vm_name_list, action='start')
    mini.vm_ops(vm_name_list, action='reboot')
    mini.check_browser_console_log()
    test_util.test_pass('Start, Stop and Reboot VMs in Batches Successful')


def env_recover():
    global mini
    mini.expunge_vm(vm_name_list)
    mini.close()

#Will be called only if exception happens in test().
def error_cleanup():
    global mini
    try:
        mini.expunge_vm(vm_name_list)
        mini.close()
    except:
        pass
