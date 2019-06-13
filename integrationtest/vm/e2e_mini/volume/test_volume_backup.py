# -*- coding:utf-8 -*-

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib

test_stub = test_lib.lib_get_test_stub()

mini = None
volume_name = 'volume-' + test_stub.get_time_postfix()
backup_name = 'backup-' + test_stub.get_time_postfix()

def test():
    global mini
    mini = test_stub.MINI()
    mini.create_vm()
    mini.create_volume(volume_name, 'volume')
    mini.volume_attach_to_vm()
    mini.create_backup(volume_name, 'volume', backup_name)
    mini.vm_ops(mini.vm_name, action='stop')
    mini.restore_backup(volume_name, 'volume', backup_name)
    mini.delete_backup(volume_name, 'volume', backup_name)
    mini.check_browser_console_log()
    test_util.test_pass('Test Volume Create, Restore and Delete Backups Successful')


def env_recover():
    global mini
    mini.expunge_vm()
    mini.expunge_volume(volume_name)
    mini.close()

#Will be called only if exception happens in test().
def error_cleanup():
    global mini
    try:
        mini.expunge_vm()
        mini.expunge_volume(volume_name)
        mini.close()
    except:
        pass
