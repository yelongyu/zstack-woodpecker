'''

New Integration Test for Simple VM stop/start scheduler update.

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
schd1 = None
schd2 = None


def test():
    global vm
    global schd1
    global schd2
    vm = test_stub.create_vlan_vm(os.environ.get('l3VlanNetworkName1'))
    start_date = int(time.time())
    test_util.test_logger('Setup stop and start VM scheduler')
    schd1 = vm_ops.stop_vm_scheduler(vm.get_vm().uuid, 'simple', 'simple_stop_vm_scheduler', start_date, 1)
    schd2 = vm_ops.start_vm_scheduler(vm.get_vm().uuid, 'simple', 'simple_start_vm_scheduler', start_date, 2)
    test_stub.sleep_util(start_date+58)

    stop_msg_mismatch = 0
    start_msg_mismatch = 0
    for i in range(0, 58):
        if not test_lib.lib_find_in_local_management_server_log(start_date+i, 'StopVmInstanceMsg', vm.get_vm().uuid):
            stop_msg_mismatch += 1
            test_util.test_warn('StopVmInstanceMsg is expected to execute at %s' % (start_date+i))
        if i % 2 == 0:
            if not test_lib.lib_find_in_local_management_server_log(start_date+i, 'StartVmInstanceMsg', vm.get_vm().uuid):
                start_msg_mismatch += 1
                test_util.test_warn('StartVmInstanceMsg is expected to execute at %s' % (start_date+i))
        else:
            if test_lib.lib_find_in_local_management_server_log(start_date+i, 'StartVmInstanceMsg', vm.get_vm().uuid):
                start_msg_mismatch += 1
                test_util.test_warn('StartVmInstanceMsg is not expected to execute at %s' % (start_date+i))

    if stop_msg_mismatch > 5:
        test_util.test_fail('%s of 58 StopVmInstanceMsg not executed at expected timestamp' % (stop_msg_mismatch))

    if start_msg_mismatch > 5:
        test_util.test_fail('%s of 58 StartVmInstanceMsg not executed at expected timestamp' % (start_msg_mismatch))

    test_util.test_logger('Update stop and start VM scheduler to start after 500 seconds')
    start_date = int(time.time())
    schd_ops.update_scheduler(schd1.uuid, 'simple', 'simple_stop_vm_scheduler2', start_date+60, 2, repeatCount=None)
    schd_ops.update_scheduler(schd2.uuid, 'simple', 'simple_start_vm_scheduler2', start_date+60, 1, repeatCount=None)
    test_stub.sleep_util(start_date+59)

    for i in range(0, 58):
        if test_lib.lib_find_in_local_management_server_log(start_date+i, 'StopVmInstanceMsg', vm.get_vm().uuid):
            test_util.test_fail('StopVmInstanceMsg is not expected to execute at %s' % (start_date+i))
        if test_lib.lib_find_in_local_management_server_log(start_date+i, 'StartVmInstanceMsg', vm.get_vm().uuid):
            test_util.test_fail('StartVmInstanceMsg is not expected to execute at %s' % (start_date+i))
   
    test_stub.sleep_util(start_date+120)
    stop_msg_mismatch = 0
    start_msg_mismatch = 0
    for i in range(0, 58):
        if i % 2 == 0:
            if not test_lib.lib_find_in_local_management_server_log(start_date+60+i, 'StopVmInstanceMsg', vm.get_vm().uuid):
                stop_msg_mismatch += 1
                test_util.test_warn('StopVmInstanceMsg is expected to execute at %s' % (start_date+60+i))
        else:
            if test_lib.lib_find_in_local_management_server_log(start_date+60+i, 'StopVmInstanceMsg', vm.get_vm().uuid):
                stop_msg_mismatch += 1
                test_util.test_warn('StopVmInstanceMsg is not expected to execute at %s' % (start_date+60+i))

        if not test_lib.lib_find_in_local_management_server_log(start_date+60+i, 'StartVmInstanceMsg', vm.get_vm().uuid):
                start_msg_mismatch += 1
                test_util.test_warn('StartVmInstanceMsg is expected to execute at %s' % (start_date+60+i))

    if stop_msg_mismatch > 5:
        test_util.test_fail('%s of 58 StopVmInstanceMsg not executed at expected timestamp' % (stop_msg_mismatch))

    if start_msg_mismatch > 5:
        test_util.test_fail('%s of 58 StartVmInstanceMsg not executed at expected timestamp' % (start_msg_mismatch))

    schd_ops.delete_scheduler(schd1.uuid)
    schd_ops.delete_scheduler(schd2.uuid)
    vm.destroy()
    test_util.test_pass('Create Simple VM Stop Start Scheduler Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global vm
    global schd1
    global schd2

    if vm:
        vm.destroy()

    if schd1:
	schd_ops.delete_scheduler(schd1.uuid)

    if schd2:
	schd_ops.delete_scheduler(schd2.uuid)
