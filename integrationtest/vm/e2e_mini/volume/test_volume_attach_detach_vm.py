# -*- coding:utf-8 -*-

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import volume

vm_ops = None
volume_ops = None

def test():
    global vm_ops
    global volume_ops
    volume_ops = volume.VOLUME()
    vm = test_lib.lib_get_specific_stub(suite_name='e2e_mini/vm', specific_name='vm')
    vm_ops = vm.VM(uri=volume_ops.uri, initialized=True)
    volume_ops.create_volume()
    vm_ops.create_vm()
    volume_ops.volume_attach_to_vm(dest_vm=vm_ops.vm_name, details_page=True)
    volume_ops.volume_detach_from_vm()
    vm_ops.check_browser_console_log()
    test_util.test_pass('Test Volume to Attach VM and Detach VM Successful')


def env_recover():
    global vm_ops
    global volume_ops
    vm_ops.delete_vm()
    volume_ops.delete_volume()
    vm_ops.close()

#Will be called only if exception happens in test().
def error_cleanup():
    global vm_ops
    global volume_ops
    try:
        vm_ops.delete_vm()
        volume_ops.delete_volume()
        vm_ops.close()
    except:
        pass
