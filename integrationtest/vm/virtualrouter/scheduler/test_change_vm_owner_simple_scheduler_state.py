'''

@author: MengLai
'''

import os
import time
import zstackwoodpecker.operations.vm_operations as vm_ops
import zstackwoodpecker.operations.scheduler_operations as schd_ops
import zstackwoodpecker.operations.account_operations as account_operations
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops

test_stub = test_lib.lib_get_test_stub()
vm = None
schd_job1 = None
schd_job2 = None
schd_trigger1 = None
schd_trigger2 = None

def check_scheduler_state(schd, target_state):
    conditions = res_ops.gen_query_conditions('uuid', '=', schd.uuid)
    schd_state = res_ops.query_resource(res_ops.SCHEDULERJOB, conditions)[0].state
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
    global schd_job1
    global schd_job2
    global schd_trigger1
    global schd_trigger2
    global new_account

    vm = test_stub.create_vlan_vm(os.environ.get('l3VlanNetworkName1'))
    start_date = int(time.time())
    schd_job1 = schd_ops.create_scheduler_job('simple_stop_vm_scheduler', 'simple_stop_vm_scheduler', vm.get_vm().uuid, 'stopVm', None)
    schd_trigger1 = schd_ops.create_scheduler_trigger('simple_stop_vm_scheduler', start_date+30, None, 60, 'simple')
    schd_ops.add_scheduler_job_to_trigger(schd_trigger1.uuid, schd_job1.uuid)
    #schd1 = vm_ops.stop_vm_scheduler(vm.get_vm().uuid, 'simple', 'simple_stop_vm_scheduler', start_date+30, 60)

    schd_job2 = schd_ops.create_scheduler_job('simple_start_vm_scheduler', 'simple_start_vm_scheduler', vm.get_vm().uuid, 'startVm', None)
    schd_trigger2 = schd_ops.create_scheduler_trigger('simple_start_vm_scheduler', start_date+60, None, 60, 'simple')
    schd_ops.add_scheduler_job_to_trigger(schd_trigger2.uuid, schd_job2.uuid)
    #schd2 = vm_ops.start_vm_scheduler(vm.get_vm().uuid, 'simple', 'simple_start_vm_scheduler', start_date+60, 60)

    test_stub.sleep_util(start_date+130)

    test_util.test_dsc('check scheduler state after creating scheduler')
    check_scheduler_state(schd_job1, 'Enabled')
    check_scheduler_state(schd_job2, 'Enabled')
    if not check_scheduler_msg('run scheduler for job: StopVmInstanceJob', start_date+30):
        test_util.test_fail('StopVmInstanceJob not executed at expected timestamp range')
    if not check_scheduler_msg('run scheduler for job: StartVmInstanceJob', start_date+60):
        test_util.test_fail('StartVmInstanceJob not executed at expected timestamp range')
    
#    vm.check();
    new_account = account_operations.create_account('new_account', 'password', 'Normal')

    res_ops.change_recource_owner(new_account.uuid, vm.vm.uuid)

    current_time = int(time.time())
    except_start_time =  start_date + 60 * (((current_time - start_date) % 60) + 1)
    test_stub.sleep_util(except_start_time + 130)
 
    test_util.test_dsc('check scheduler state after changing the owner of vm')
    check_scheduler_state(schd_job1, 'Enabled')
    check_scheduler_state(schd_job2, 'Enabled')
    if not check_scheduler_msg('run scheduler for job: StopVmInstanceJob', except_start_time+30):
        test_util.test_fail('StopVmInstanceJob executed at unexpected timestamp range')
    if not check_scheduler_msg('run scheduler for job: StartVmInstanceJob', except_start_time+60):
        test_util.test_fail('StartVmInstanceJob executed at unexpected timestamp range')

    schd_ops.del_scheduler_job(schd_job1.uuid)
    schd_ops.del_scheduler_trigger(schd_trigger1.uuid)
    schd_ops.del_scheduler_job(schd_job2.uuid)
    schd_ops.del_scheduler_trigger(schd_trigger2.uuid)
    vm.destroy()
    account_operations.delete_account(new_account.uuid)

    test_util.test_pass('Check Scheduler State after Changing VM Owner Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global vm
    global schd_job1
    global schd_job2
    global schd_trigger1
    global schd_trigger2
    global new_account
 
    if vm:
        vm.destroy()

    if schd_job1:
	schd_ops.del_scheduler_job(schd_job1.uuid)
    if schd_trigger1:
	schd_ops.del_scheduler_trigger(schd_trigger1.uuid)
    if schd_job2:
	schd_ops.del_scheduler_job(schd_job2.uuid)
    if schd_trigger2:
	schd_ops.del_scheduler_trigger(schd_trigger2.uuid)

    if new_account:
       account_operations.delete_account(new_account.uuid) 
