# -*- coding:utf-8 -*-

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib

test_stub = test_lib.lib_get_test_stub()

mini = None
vm_name = 'vm-' + test_stub.get_time_postfix()

def test():
    global mini
    global vm_name
    mini = test_stub.MINI()
    mini.create_vm(name=vm_name)
    mini.create_volume(vm=vm_name, provisioning=u'厚置备', view='list')
    mini.create_volume(vm=vm_name, provisioning=u'精简置备', view='list')
    mini.check_browser_console_log()
    test_util.test_pass('Create Volume Attached VM Successful')


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
