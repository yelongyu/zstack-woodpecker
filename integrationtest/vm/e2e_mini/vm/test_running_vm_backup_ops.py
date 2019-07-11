# -*- coding:utf-8 -*-

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import vm

vm_ops = None
vm_name = 'vm-' + vm.get_time_postfix()
backup_list = ['backup-' + vm.get_time_postfix() for _ in range(2)]

def test():
    global vm_ops
    vm_ops = vm.VM()
    vm_ops.create_vm(vm_name, 'vm')
    vm_ops.create_backup(vm_name, 'vm', backup_list[0])
    vm_ops.create_backup(vm_name, 'vm', backup_list[1])
    vm_ops.vm_ops(vm_name, action='stop')
    vm_ops.restore_backup(vm_name, 'vm', backup_list[0])
    vm_ops.restore_backup(vm_name, 'vm', backup_list[1])
    vm_ops.vm_ops(vm_name, 'start')
    vm_ops.delete_backup(vm_name, 'vm', backup_list)
    vm_ops.check_browser_console_log()
    test_util.test_pass('Test VM Create, Restore and Delete Backups Successful')


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
