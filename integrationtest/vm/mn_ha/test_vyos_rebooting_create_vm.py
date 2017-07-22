'''
Test for tracking http://dev.zstack.io/browse/ZSTAC-5595
@author: SyZhao
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.node_operations as node_ops
import zstackwoodpecker.zstack_test.zstack_test_vm as test_vm_header
import zstackwoodpecker.operations.vm_operations as vm_ops
import test_stub
import threading

vm = None
vm2 = None

def async_exec_reboot_vr(uuid):
    vm_ops.reboot_vm(uuid)


def test():
    global vm, vm2
    test_stub.skip_if_vr_not_vyos("vr")
    test_lib.clean_up_all_vr()
    vm = test_stub.create_basic_vm()
    vm.check()
    vr_vm = test_lib.lib_find_vr_by_vm(vm.vm)[0]
    vm.destroy()

    t = threading.Thread(target=async_exec_reboot_vr, args=(vr_vm.uuid,))
    t.start()

    vm2 = test_stub.create_basic_vm(wait_vr_running=False)
    vm2.check()
    vm2.destroy()

    test_util.test_pass('Create VM when vyos is rebooting Test Success')

#Will be called what ever test result is
def env_recover():
    pass

#Will be called only if exception happens in test().
def error_cleanup():
    global vm,vm2
    if vm:
        try:
            vm2.destroy()
            vm.destroy()
        except:
            pass
