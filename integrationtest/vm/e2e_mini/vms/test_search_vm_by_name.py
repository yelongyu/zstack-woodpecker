# -*- coding:utf-8 -*-

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib

test_stub = test_lib.lib_get_test_stub()

mini = None
vm_name_list = [u'vm-一', 'vm-one', 'vm-1']
search_value_list = ['oNe', '1', u'一', 'vm', '-']

def test():
    global mini

    mini = test_stub.MINI()
    for vm_name in vm_name_list:
        mini.create_vm(name=vm_name)
    # search in existing vms
    for search_value in search_value_list:
        mini.search(search_value, not_null=True)
    mini.delete_vm(vm_name_list, corner_btn=False)
    # search in deleted vms
    for search_value in search_value_list:
        mini.search(search_value, tab_name=u'已删除', not_null=True)
    mini.check_browser_console_log()
    test_util.test_pass('Test Search VM By Name Successful')


def env_recover():
    global mini
    mini.expunge_vm()
    mini.close()

#Will be called only if exception happens in test().
def error_cleanup():
    global mini
    try:
        mini.expunge_vm()
        mini.close()
    except:
        pass
