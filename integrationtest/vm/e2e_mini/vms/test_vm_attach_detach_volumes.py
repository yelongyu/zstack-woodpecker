# -*- coding:utf-8 -*-

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib

test_stub = test_lib.lib_get_test_stub()

mini = None
vm_name = 'vm-' + test_stub.get_time_postfix()
volume_list = ['volume-' + test_stub.get_time_postfix() for _ in range(2)]

def test():
    global mini
    mini = test_stub.MINI()
    mini.create_vm(vm_name)
    for vol in volume_list:
        mini.create_volume(vol)
    mini.vm_attach_volume(vm_name, volume_list)
    mini.vm_detach_volume(vm_name, volume_list)
    mini.check_browser_console_log()
    test_util.test_pass('Test VM Attach and Detach Volumes Successful')


def env_recover():
    global mini
    mini.delete_vm(vm_name)
    mini.delete_volume(volume_list)
    mini.close()

#Will be called only if exception happens in test().
def error_cleanup():
    global mini
    try:
        mini.delete_vm(vm_name)
        mini.delete_volume(volume_list)
        mini.close()
    except:
        pass
