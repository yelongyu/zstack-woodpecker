# -*- coding:utf-8 -*-

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib

test_stub = test_lib.lib_get_test_stub()

mini = None
vm_name = 'vm-' + test_stub.get_time_postfix()
backup_list = ['backup-' + test_stub.get_time_postfix() for _ in range(2)]

def test():
    global mini
    mini = test_stub.MINI()
    mini.create_vm(vm_name, 'vm')
    mini.create_backup(vm_name, 'vm', backup_list[0])
    mini.create_backup(vm_name, 'vm', backup_list[1])
    mini.vm_ops(vm_name, action='stop')
    mini.restore_backup(vm_name, 'vm', backup_list[0])
    mini.restore_backup(vm_name, 'vm', backup_list[1])
    mini.delete_backup(vm_name, 'vm', backup_list)
    mini.check_browser_console_log()
    test_util.test_pass('Test VM Create, Restore and Delete Backups Successful')


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
