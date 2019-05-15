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
    mini.set_ha_level(name=vm_name, ha=True)
    mini.set_ha_level(name=vm_name, ha=False)
    mini.set_ha_level(name=vm_name, ha=True, details_page=True)
    mini.set_ha_level(name=vm_name, ha=False, details_page=True)
    mini.check_browser_console_log()
    test_util.test_pass('Set VM HA Level Successful')


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
