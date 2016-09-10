'''

@author: MengLai
'''

import os
import time
import zstackwoodpecker.operations.vm_operations as vm_ops
import zstackwoodpecker.operations.scheduler_operations as schd_ops
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops

test_stub = test_lib.lib_get_test_stub()
vm = None
schd1 = None
schd2 = None

def check_scheduler_state(schd,target_state):
    conditions = res_ops.gen_query_conditions('uuid', '=', schd.uuid)
    schd_state = res_ops.query_resource(res_ops.SCHEDULER, conditions)[0].state
    if schd_state != target_state:
        test_util.test_fail('check scheduler state, it is expected to be %s, but it is %s' % (target_state, schd_state))

    return True        

def check_scheduler_msg(msg, timestamp):
    msg_mismatch = 0
    for i in range(0, 20):
        if test_lib.lib_find_in_local_management_server_log(timestamp + i, msg, vm.get_vm().uuid):
            msg_mismatch = 1
            return True

    if msg_mismatch == 0:
        return False

def test():
    global vm
    global schd1
    global schd2

    vm = test_stub.create_vlan_vm(os.environ.get('l3VlanNetworkName1'))
    start_date = int(time.time())
    schd1 = vm_ops.stop_vm_scheduler(vm.get_vm().uuid, 'simple', 'simple_stop_vm_scheduler', start_date+10, 20)
    schd2 = vm_ops.start_vm_scheduler(vm.get_vm().uuid, 'simple', 'simple_start_vm_scheduler', start_date+20, 20)

    test_stub.sleep_util(start_date+45)

    test_util.test_dsc('check scheduler state after create scheduler')
    check_scheduler_state(schd1, 'Enabled')
    check_scheduler_state(schd2, 'Enabled')
    if not check_scheduler_msg('run scheduler for job: StopVmInstanceJob', start_date+10):
        test_util.test_fail('StopVmInstanceJob not executed at expected timestamp range')
    if not check_scheduler_msg('run scheduler for job: StartVmInstanceJob', start_date+20):
        test_util.test_fail('StartVmInstanceJob not executed at expected timestamp range')

    schd_ops.change_scheduler_state(schd1.uuid, 'disable')
    schd_ops.change_scheduler_state(schd2.uuid, 'disable')

    test_stub.sleep_util(20)
   
    current_time = int(time.time())
    except_start_time =  start_date + 20 * (((current_time - start_date) % 20) + 1) 
    test_stub.sleep_util(except_start_time+45)
 
    test_util.test_dsc('check scheduler state after pause scheduler')
    check_scheduler_state(schd1, 'Disabled')
    check_scheduler_state(schd2, 'Disabled')
    if check_scheduler_msg('run scheduler for job: StopVmInstanceJob', except_start_time+10):
        test_util.test_fail('StopVmInstanceJob executed at unexpected timestamp range')
    if check_scheduler_msg('run scheduler for job: StartVmInstanceJob', except_start_time+20):
        test_util.test_fail('StartVmInstanceJob executed at unexpected timestamp range')

    schd_ops.change_scheduler_state(schd1.uuid, 'enable')
    schd_ops.change_scheduler_state(schd2.uuid, 'enable')

    test_stub.sleep_util(20)

    current_time = int(time.time())
    except_start_time =  start_date + 20 * (((current_time - start_date) % 20) + 1)
    test_stub.sleep_util(except_start_time+45)

    test_util.test_dsc('check scheduler state after resume scheduler')
    check_scheduler_state(schd1, 'Enabled')
    check_scheduler_state(schd2, 'Enabled')
    if not check_scheduler_msg('run scheduler for job: StopVmInstanceJob', except_start_time+10):
        test_util.test_fail('StopVmInstanceJob not executed at expected timestamp range')
    if not check_scheduler_msg('run scheduler for job: StartVmInstanceJob', except_start_time+20):
        test_util.test_fail('StartVmInstanceJob not executed at expected timestamp range')

    schd_ops.delete_scheduler(schd1.uuid)
    schd_ops.delete_scheduler(schd2.uuid)
    vm.destroy()
    test_util.test_pass('Check Scheduler State after Pause and Resume Scheduler Success')

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
