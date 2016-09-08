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
    if not test_lib.lib_find_in_local_management_server_log(timestamp, msg, vm.get_vm().uuid):
        return False

    return True

def test():
    global vm
    global schd1
    global schd2

    vm = test_stub.create_vlan_vm(os.environ.get('l3VlanNetworkName1'))
    start_date = int(time.time())
    schd1 = vm_ops.stop_vm_scheduler(vm.get_vm().uuid, 'simple', 'simple_stop_vm_scheduler', start_date+60, 120)
    schd2 = vm_ops.start_vm_scheduler(vm.get_vm().uuid, 'simple', 'simple_start_vm_scheduler', start_date+120, 120)

    test_stub.sleep_util(start_date+125)

    test_util.test_dsc('check scheduler state after create scheduler')
    check_scheduler_state(schd1, 'Enabled')
    check_scheduler_state(schd2, 'Enabled')
#    if not check_scheduler_msg('[msg received]: {"org.zstack.header.vm.StopVmInstanceMsg', start_date+60):
#        test_util.test_fail('StopVmInstanceMsg not executed at expected timestamp %s' % start_date+60)
#    if not check_scheduler_msg('[msg received]: {"org.zstack.header.vm.StartVmInstanceMsg', start_date+120):
#        test_util.test_fail('StartVmInstanceMsg not executed at expected timestamp %s ' % start_date+120)

    schd_ops.change_scheduler_state(schd1.uuid, 'disable')
   
    current_time = int(time.time())
    except_start_time =  start_date + 120 * (((current_time - start_date) % 120) + 1) 
    test_stub.sleep_util(except_start_time+5)
 
    test_util.test_dsc('check scheduler state after pause scheduler')
    check_scheduler_state(schd1, 'Disabled')
    check_scheduler_state(schd2, 'Disabled')
#    if check_scheduler_msg('[msg received]: {"org.zstack.header.vm.StopVmInstanceMsg', except_start_time+60):
#        test_util.test_fail('StopVmInstanceMsg executed at unexpected timestamp %s' % except_start_time+60)
#    if check_scheduler_msg('[msg received]: {"org.zstack.header.vm.StartVmInstanceMsg', except_start_time+120):
#        test_util.test_fail('StartVmInstanceMsg executed at unexpected timestamp %s ' % except_start_time+120)

    schd_ops.change_scheduler_state(schd1.uuid, 'enable')

    current_time = int(time.time())
    except_start_time =  start_date + 120 * (((current_time - start_date) % 120) + 1)
    test_stub.sleep_util(except_start_time+5)

    test_util.test_dsc('check scheduler state after resume scheduler')
    check_scheduler_state(schd1, 'Enabled')
    check_scheduler_state(schd2, 'Enabled')
#    if not check_scheduler_msg('[msg received]: {"org.zstack.header.vm.StopVmInstanceMsg', except_start_time+60):
#        test_util.test_fail('StopVmInstanceMsg not executed at expected timestamp %s' % except_start_time+60)
#    if not check_scheduler_msg('[msg received]: {"org.zstack.header.vm.StartVmInstanceMsg', except_start_time+120):
#        test_util.test_fail('StartVmInstanceMsg not executed at expected timestamp %s ' % except_start_time+120)

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
