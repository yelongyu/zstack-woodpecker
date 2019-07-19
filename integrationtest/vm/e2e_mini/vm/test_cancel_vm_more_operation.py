# -*- coding:utf-8 -*-

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib

vm = test_lib.lib_get_specific_stub('e2e_mini/vm', 'vm')

vm_ops = None
vm_name = 'vm-' + vm.get_time_postfix()
op_list = {u'重启', u'高可用', u'修改信息'}

def test():
    global vm_ops
    vm_ops = vm.VM()
    vm_ops.create_vm(name=vm_name)
    for op in op_list:
        vm_ops.cancel_more_operation(op_name=op, res_name=vm_name, res_type='vm', details_page=False, close=False)
        vm_ops.cancel_more_operation(op_name=op, res_name=vm_name, res_type='vm', details_page=False, close=True)
        vm_ops.cancel_more_operation(op_name=op, res_name=vm_name, res_type='vm', details_page=True, close=False)
        vm_ops.cancel_more_operation(op_name=op, res_name=vm_name, res_type='vm', details_page=True, close=True)
    vm_ops.check_browser_console_log()
    test_util.test_pass('Cancel VM More Operation Successful')


def env_recover():
    global vm_ops
    vm_ops.expunge_vm(vm_name)
    vm_ops.close()

#Will be called only if exception happens in test().
def error_cleanup():
    global vm_ops
    try:
        vm_ops.expunge_vm(vm_name)
        vm_ops.close()
    except:
        pass