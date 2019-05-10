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
    mini.delete_vm(vm_name_list, corner_btn=False)
    mini.resume(vm_name_list, 'vm')
    test_util.test_pass('Create VM Successful')


def env_recover():
    global mini
    mini.delete_vm(vm_name_list, corner_btn=False)
    mini.expunge_vm(vm_name_list)
    mini.close()

#Will be called only if exception happens in test().
def error_cleanup():
    global mini
    try:
        mini.delete_vm(vm_name_list, corner_btn=False)
        mini.expunge_vm(vm_name_list)
        mini.close()
    except:
        pass
