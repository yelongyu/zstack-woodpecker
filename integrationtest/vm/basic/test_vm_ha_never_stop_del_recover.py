'''

New Integration Test for VM ha never stop with delete and recover

@author: quarkonics
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import test_stub
import zstackwoodpecker.header.vm as vm_header
import zstackwoodpecker.operations.ha_operations as ha_ops
import time

vm = None
delete_policy = None

def test():
    global vm
    if test_lib.lib_get_ha_enable() != 'true':
        test_util.test_skip("vm ha not enabled. Skip test")

    delete_policy = test_lib.lib_get_delete_policy('vm')
    vm = test_stub.create_vm()
    vm.set_delete_policy('Delay')
    vm.check()
    ha_ops.set_vm_instance_ha_level(vm.get_vm().uuid, "NeverStop")
    vm.destroy()
    vm.recover()
    time.sleep(60)
    vm.set_state(vm_header.STOPPED)
    vm.check()
    vm.destroy()
    vm.set_delete_policy(delete_policy)
    test_util.test_pass('VM ha never stop with delete and recover Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global delete_policy
    global vm
    vm.set_delete_policy(delete_policy)
    if vm:
        vm.destroy()
