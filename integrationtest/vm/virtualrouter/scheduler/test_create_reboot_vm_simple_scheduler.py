'''

New Integration Test for Simple VM reboot scheduler.

@author: quarkonics
'''

import os
import time
import zstackwoodpecker.operations.vm_operations as vm_ops
import zstackwoodpecker.operations.scheduler_operations as schd_ops
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
test_stub = test_lib.lib_get_test_stub()
vm = None
schd = None


def test():
    global vm
    global schd
    vm = test_stub.create_vlan_vm(os.environ.get('l3VlanNetworkName1'))
    start_date = int(time.time())
    schd = vm_ops.stop_vm_scheduler(vm.get_vm().uuid, 'simple', 'simple_reboot_vm_scheduler', start_date+60, 120)
    test_stub.sleep_util(start_date+58)
    for i in range(0, 58)
        if test_lib.lib_find_in_local_management_server_log(start_date+i, '[msg received]: {"org.zstack.header.vm.RebootVmInstanceMsg', vm.get_vm().uuid):
            test_util.test_fail('VM is expected to reboot start from %s' (start_date+60))

    test_stub.sleep_util(start_date+59)

    if not test_lib.lib_wait_target_down(vr_mgmt_ip, '7272', 60):
        test_util.test_fail('VM: %s is not reboot in 60 seconds. Fail to reboot it with scheduler. ' % vm.get_vm().uuid)

    if not test_lib.lib_find_in_local_management_server_log(start_date+60, '[msg received]: {"org.zstack.header.vm.RebootVmInstanceMsg', vm.get_vm().uuid):
        test_util.test_fail('VM is expected to reboot start from %s' (start_date+60))

    schd_ops.delete_scheduler(schd.uuid)
    vm.destroy()
    test_util.test_pass('Create Simple VM Reboot Scheduler Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global vm
    global schd

    if vm:
        vm.destroy()

    if schd:
	schd_ops.delete_scheduler(schd.uuid)
