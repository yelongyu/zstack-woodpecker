'''

New Integration Test for Simple VM stop/start scheduler.

@author: MengLai
'''

import os
import time
import zstackwoodpecker.operations.vm_operations as vm_ops
import zstackwoodpecker.operations.scheduler_operations as schd_ops
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops

_config_ = {
        'timeout' : 2000,
        'noparallel' : True
        }

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

    delete_policy = test_lib.lib_get_delete_policy('vm')
    vm = test_stub.create_vlan_vm(os.environ.get('l3VlanNetworkName1'))
    vm.set_delete_policy('Delay')

    start_date = int(time.time())
    schd_job1 = schd_ops.create_scheduler_job('simple_stop_vm_scheduler', 'simple_stop_vm_scheduler', vm.get_vm().uuid, 'stopVm', None)
    schd_trigger1 = schd_ops.create_scheduler_trigger('simple_stop_vm_scheduler', start_date+10, None, 20, 'simple')
    schd_ops.add_scheduler_job_to_trigger(schd_trigger1.uuid, schd_job1.uuid)
    #schd1 = vm_ops.stop_vm_scheduler(vm.get_vm().uuid, 'simple', 'simple_stop_vm_scheduler', start_date+10, 20)

    schd_job2 = schd_ops.create_scheduler_job('simple_start_vm_scheduler', 'simple_start_vm_scheduler', vm.get_vm().uuid, 'startVm', None)
    schd_trigger2 = schd_ops.create_scheduler_trigger('simple_start_vm_scheduler', start_date+20, None, 20, 'simple')
    schd_ops.add_scheduler_job_to_trigger(schd_trigger2.uuid, schd_job2.uuid)
    #schd2 = vm_ops.start_vm_scheduler(vm.get_vm().uuid, 'simple', 'simple_start_vm_scheduler', start_date+20, 20)

    test_stub.sleep_util(start_date+45)

    test_util.test_dsc('check scheduler state after create scheduler')
    check_scheduler_state(schd_job1, 'Enabled')
    check_scheduler_state(schd_job2, 'Enabled')
    if not check_scheduler_msg('run scheduler for job: StopVmInstanceJob', start_date+10):
        test_util.test_fail('StopVmInstanceJob not executed at expected timestamp range')
    if not check_scheduler_msg('run scheduler for job: StartVmInstanceJob', start_date+20):
        test_util.test_fail('StartVmInstanceJob not executed at expected timestamp range')

    vm.destroy()

    current_time = int(time.time())
    except_start_time =  start_date + 20 * (((current_time - start_date) % 20) + 1)
    test_stub.sleep_util(except_start_time + 45)

    test_util.test_dsc('check scheduler state after destroy vm')
    check_scheduler_state(schd_job1, 'Disabled')
    check_scheduler_state(schd_job2, 'Disabled')
    if check_scheduler_msg('run scheduler for job: StopVmInstanceJob', except_start_time+10):
        test_util.test_fail('StopVmInstanceJob executed at unexpected timestamp range')
    if check_scheduler_msg('run scheduler for job: StartVmInstanceJob', except_start_time+20):
        test_util.test_fail('StartVmInstanceJob executed at unexpected timestamp range')

    vm.recover()

    current_time = int(time.time())
    except_start_time =  start_date + 20 * (((current_time - start_date) % 20) + 1)
    test_stub.sleep_util(except_start_time + 45)

    test_util.test_dsc('check scheduler state after recover vm')
    check_scheduler_state(schd_job1, 'Disabled')
    check_scheduler_state(schd_job2, 'Disabled')
#    if not check_scheduler_msg('run scheduler for job: StopVmInstanceJob', except_start_time+10):
#        test_util.test_fail('StopVmInstanceJob not executed at expected timestamp range')
#    if not check_scheduler_msg('run scheduler for job: StartVmInstanceJob', except_start_time+20):
#        test_util.test_fail('StartVmInstanceJob not executed at expected timestamp range' )

    schd_ops.del_scheduler_job(schd_job1.uuid)
    schd_ops.del_scheduler_trigger(schd_trigger1.uuid)
    schd_ops.del_scheduler_job(schd_job2.uuid)
    schd_ops.del_scheduler_trigger(schd_trigger2.uuid)

    vm.set_delete_policy(delete_policy)
    vm.destroy()

    conditions = res_ops.gen_query_conditions('uuid', '=', schd_job1.uuid)
    if len(res_ops.query_resource(res_ops.SCHEDULERJOB, conditions)) > 0:
        test_util.test_fail('check stop vm scheduler, it is expected to be destroied, but it still exists')
   
    conditions = res_ops.gen_query_conditions('uuid', '=', schd_job2.uuid)
    if len(res_ops.query_resource(res_ops.SCHEDULERJOB, conditions)) > 0:
        test_util.test_fail('check start vm scheduler, it is expected to be destroied, but it still exists')

    test_util.test_pass('Check Scheduler State after Destroy and Recover VM Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global vm
    global schd_job1
    global schd_job2
    global schd_trigger1
    global schd_trigger2

    vm.set_delete_policy(delete_policy)
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
