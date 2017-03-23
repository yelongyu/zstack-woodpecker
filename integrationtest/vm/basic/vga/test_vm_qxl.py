'''

New Integration Test for VM vga qxl mode.

@author: quarkonics
'''

import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.config_operations as conf_ops
import zstackwoodpecker.test_util as test_util
test_stub = test_lib.lib_get_test_stub()

_config_ = {
        'timeout' : 360,
        'noparallel' : False
        }

vm = None
default_mode = None

def test():
    global vm
    global default_mode
#    default_mode = conf_ops.get_global_config_value('kvm', 'videoType')
    default_mode = conf_ops.change_global_config('vm', 'videoType', 'qxl')
    vm = test_stub.create_vm()
    vm.check()
    vm_mode = test_lib.lib_get_vm_video_type(vm.get_vm())
    if vm_mode != 'qxl':
        test_util.test_fail('VM is expected to work in vga mode instead of %s' % (vm_mode))
    vm.destroy()
    vm.check()
    conf_ops.change_global_config('vm', 'videoType', default_mode)
    test_util.test_pass('Create VM Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    conf_ops.change_global_config('vm', 'videoType', default_mode)
    global vm
    if vm:
        vm.destroy()
