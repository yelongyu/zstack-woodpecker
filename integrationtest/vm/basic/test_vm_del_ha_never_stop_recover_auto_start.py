'''

New Integration Test for VM ha never stop auto start with recover

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
    vm = test_stub.create_vm()
    vm.check()
    delete_policy = test_lib.lib_set_delete_policy('vm', 'Delay')
    vm.destroy()
    ha_ops.set_vm_instance_ha_level(vm.get_vm().uuid, "NeverStop")
    vm.recover()
    time.sleep(60)
    vm.set_state(vm_header.RUNNING)
    vm.check()
    vm.destroy()
    test_lib.lib_set_delete_policy('vm', delete_policy)
    test_util.test_pass('VM ha never stop auto start with recover Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global delete_policy
    test_lib.lib_set_delete_policy('vm', delete_policy)
    global vm
    if vm:
        vm.destroy()
