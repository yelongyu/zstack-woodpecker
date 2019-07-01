# -*- coding:utf-8 -*-

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib

vm = test_lib.lib_get_specific_stub(suite_name='e2e_mini/vms', specific_name='vm')
volume = test_lib.lib_get_specific_stub(suite_name='e2e_mini/volume', specific_name='volume')

vm_ops = None
volume_ops = None
vm_name = 'vm-' + vm.get_time_postfix()

def test():
    global volume_ops
    global vm_ops
    global vm_name
    volume_ops = volume.VOLUME()
    vm_ops.create_vm(name=vm_name)
    volume_ops.create_volume(vm=vm_name, provisioning=u'厚置备', view='list')
    volume_ops.create_volume(vm=vm_name, provisioning=u'精简置备', view='list')
    volume_ops.check_browser_console_log()
    test_util.test_pass('Create Volume Attached VM Successful')


def env_recover():
    global volume_ops
    global vm_ops
    vm_ops.expunge_vm(vm_name)
    volume_ops.expunge_volume()
    volume_ops.close()

#Will be called only if exception happens in test().
def error_cleanup():
    global volume_ops
    global vm_ops
    try:
        vm_ops.expunge_vm(vm_name)
        volume_ops.expunge_volume()
        volume_ops.close()
    except:
        pass
