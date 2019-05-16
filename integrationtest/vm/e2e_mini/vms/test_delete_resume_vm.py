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

    for view in ['card', 'list']:
        # Delete button
        mini.delete_vm(vm_name, view=view)
        # Resume button
        mini.resume(vm_name, 'vm', view=view)

        # Delete via more operation
        mini.delete_vm(vm_name, view=view, corner_btn=False)
        # Resume by more ops
        mini.resume(vm_name, 'vm', view=view, details_page=True)

        # Delete via more operation in details page
        mini.delete_vm(vm_name, view=view, details_page=True)
    mini.check_browser_console_log()
    test_util.test_pass('Delete Resume VM Test Successful')


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
