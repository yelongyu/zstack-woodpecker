'''

New Integration Test for VM ha never stop operation with host disabled

@author: quarkonics
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.header.vm as vm_header
import zstackwoodpecker.operations.ha_operations as ha_ops
import zstackwoodpecker.operations.host_operations as host_ops
import time

test_stub = test_lib.lib_get_specific_stub()

vm = None

def test():
    global vm
    if test_lib.lib_get_ha_enable() != 'true':
        test_util.test_skip("vm ha not enabled. Skip test")

    vm = test_stub.create_vm()
    vm.check()
    host_uuid = test_lib.lib_find_host_by_vm(vm.get_vm()).uuid
    host_ops.change_host_state(host_uuid, "disable")
    time.sleep(10)
    ha_ops.set_vm_instance_ha_level(vm.get_vm().uuid, "NeverStop")
    vm.stop()
    time.sleep(60)
    vm.check()
    vm.destroy()
    vm.check()
    host_ops.change_host_state(host_uuid, "enable")
    time.sleep(60)
    test_util.test_pass('VM ha never stop Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    host_ops.change_host_state(host_uuid, "enable")
    time.sleep(60)
    global vm
    if vm:
        vm.destroy()

