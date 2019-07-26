# -*- coding:utf-8 -*-

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib

volume = test_lib.lib_get_specific_stub('e2e_mini/volume', 'volume')

volume_ops = None
vm_ops = None
volume_name = 'volume-' + volume.get_time_postfix()
backup_name = 'backup-' + volume.get_time_postfix()

def test():
    global volume_ops
    volume_ops = volume.VOLUME()
    vm = test_lib.lib_get_specific_stub(suite_name='e2e_mini/vm', specific_name='vm')
    vm_ops = vm.VM(uri=volume_ops.uri, initialized=True)
    vm_ops.create_vm()
    volume_ops.create_volume(volume_name)
    volume_ops.volume_attach_to_vm(vm_ops.vm_name)
    volume_ops.create_backup(volume_name, 'volume', backup_name)
    vm_ops.vm_ops(vm_ops.vm_name, action='stop')
    volume_ops.restore_backup(volume_name, 'volume', backup_name)
    volume_ops.delete_backup(volume_name, 'volume', backup_name)
    volume_ops.check_browser_console_log()
    test_util.test_pass('Test Volume Create, Restore and Delete Backups Successful')


def env_recover():
    global volume_ops
    vm_ops.expunge_vm()
    volume_ops.expunge_volume(volume_name)
    volume_ops.close()

#Will be called only if exception happens in test().
def error_cleanup():
    global volume_ops
    try:
        vm_ops.expunge_vm()
        volume_ops.expunge_volume(volume_name)
        volume_ops.close()
    except:
        pass
