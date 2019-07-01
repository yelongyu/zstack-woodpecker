# -*- coding:utf-8 -*-

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import vm

vm_ops = None
vm_name_list = [u'vm-一', 'vm-one', 'vm-1']
search_value_list = ['oNe', '1', u'一', 'vm', '-']

def test():
    global vm_ops

    vm_ops = vm.VM()
    for vm_name in vm_name_list:
        vm_ops.create_vm(name=vm_name)
    # search in existing vms
    for search_value in search_value_list:
        vm_ops.search(search_value, not_null=True)
    vm_ops.delete_vm(vm_name_list, corner_btn=False)
    # search in deleted vms
    for search_value in search_value_list:
        vm_ops.search(search_value, tab_name=u'已删除', not_null=True)
    vm_ops.check_browser_console_log()
    test_util.test_pass('Test Search VM By Name Successful')


def env_recover():
    global vm_ops
    vm_ops.expunge_vm()
    vm_ops.close()

#Will be called only if exception happens in test().
def error_cleanup():
    global vm_ops
    try:
        vm_ops.expunge_vm()
        vm_ops.close()
    except:
        pass
