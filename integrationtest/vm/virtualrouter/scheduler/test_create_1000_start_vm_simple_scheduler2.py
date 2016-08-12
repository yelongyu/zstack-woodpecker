'''

New Integration Test for Simple VM start scheduler create.

@author: quarkonics
'''

import os
import time
import sys
import threading
import zstackwoodpecker.operations.vm_operations as vm_ops
import zstackwoodpecker.operations.scheduler_operations as schd_ops
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
test_stub = test_lib.lib_get_test_stub()
vm = None
schds = []

def create_start_vm_scheduler(vm_uuid, start_date, ops_id):
    global schds
    schds.append(vm_ops.start_vm_scheduler(vm_uuid, 'simple', 'simple_start_vm_scheduler_%s' % (ops_id), start_date+100, 1000))

def delete_start_vm_scheduler(schd_uuid):
    global schds
    schd_ops.delete_scheduler(schd_uuid)

def test():
    global vm
    global schds
    vm = test_stub.create_vlan_vm(os.environ.get('l3VlanNetworkName1'))
    start_date = int(time.time())
    test_util.test_logger('Setup start VM scheduler')
    for ops_id in range(1000):
        thread = threading.Thread(target=create_start_vm_scheduler, args=(vm.get_vm().uuid, start_date, ops_id, ))
        while threading.active_count() > 10:
            time.sleep(0.5)
        exc = sys.exc_info()
        thread.start()

    while threading.activeCount() > 1:
        exc = sys.exc_info()
        time.sleep(0.1)

    test_stub.sleep_util(start_date+200)
    start_msg_mismatch = 0
    for i in range(0, 99):
        if test_lib.lib_find_in_local_management_server_log(start_date+i, '[msg send]: {"org.zstack.header.vm.StartVmInstanceMsg', vm.get_vm().uuid):
            start_msg_mismatch += 1
            test_util.test_warn('StartVmInstanceMsg is not expected to execute at %s' % (start_date+i))

    if start_msg_mismatch > 5:
        test_util.test_fail('%s of 58 StartVmInstanceMsg not executed at expected timestamp' % (start_msg_mismatch))

    count0 = test_lib.lib_count_in_local_management_server_log(start_date+100, '[msg send]: {"org.zstack.header.vm.StartVmInstanceMsg', vm.get_vm().uuid)
    test_util.test_logger('%s of 1000 scheduler executed at the same second' % count0)
    count1 = test_lib.lib_count_in_local_management_server_log(start_date+100+1, '[msg send]: {"org.zstack.header.vm.StartVmInstanceMsg', vm.get_vm().uuid)
    test_util.test_logger('%s of 1000 scheduler executed at the next second' % count1)
    count2 = test_lib.lib_count_in_local_management_server_log(start_date+100+2, '[msg send]: {"org.zstack.header.vm.StartVmInstanceMsg', vm.get_vm().uuid)
    test_util.test_logger('%s of 1000 scheduler executed at the third second' % count2)
    if count0 + count1 + count2 < 900:
        test_util.test_fail('only %s of 1000 scheduler executed at the specified first 3 seconds' % (count0 + count1 + count2))

    for schd in schds:
        thread = threading.Thread(target=delete_start_vm_scheduler, args=(schd.uuid, ))
        while threading.active_count() > 10:
            time.sleep(0.5)
        exc = sys.exc_info()
        thread.start()

    while threading.activeCount() > 1:
        exc = sys.exc_info()
        time.sleep(0.1)

    try:
        vm.destroy()
    except:
	test_util.test_logger('expected exception when destroy VM since too many queued task')
    test_util.test_pass('Create Simple VM Stop Start Scheduler Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global vm
    global schds

    if vm:
        try:
            vm.destroy()
	except:
            test_util.test_logger('expected exception when destroy VM since too many queued task')

    for schd in schds:
        thread = threading.Thread(target=delete_start_vm_scheduler, args=(schd.uuid, ))
        while threading.active_count() > 10:
            time.sleep(0.5)
        exc = sys.exc_info()
        thread.start()

    while threading.activeCount() > 1:
        exc = sys.exc_info()
        time.sleep(0.1)

