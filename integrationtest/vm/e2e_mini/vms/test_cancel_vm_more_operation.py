# -*- coding:utf-8 -*-

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib

test_stub = test_lib.lib_get_test_stub()

mini = None
vm_name = 'vm-' + test_stub.get_time_postfix()
op_list = {u'重启', u'高可用级别'}

def test():
    global mini
    mini = test_stub.MINI()
    mini.create_vm(name=vm_name)
    for op in op_list:
        mini.cancel_more_operation(op_name=op, res_name=vm_name, res_type='vm', details_page=False, close=False)
        mini.cancel_more_operation(op_name=op, res_name=vm_name, res_type='vm', details_page=False, close=True)
        mini.cancel_more_operation(op_name=op, res_name=vm_name, res_type='vm', details_page=True, close=False)
        mini.cancel_more_operation(op_name=op, res_name=vm_name, res_type='vm', details_page=True, close=True)
    mini.check_browser_console_log()
    test_util.test_pass('Cancel VM More Operation Successful')


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