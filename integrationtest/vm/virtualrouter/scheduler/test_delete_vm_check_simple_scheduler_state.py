'''

New Integration Test for Simple VM stop/start scheduler.

@author: quarkonics
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
schd1 = None
schd2 = None

def test():
    global vm
    global schd1
    global schd2

    delete_policy = test_lib.lib_get_delete_policy('vm')
    vm = test_stub.create_vlan_vm(os.environ.get('l3VlanNetworkName1'))
    vm.set_delete_policy('Delay')

    start_date = int(time.time())
    schd1 = vm_ops.stop_vm_scheduler(vm.get_vm().uuid, 'simple', 'simple_stop_vm_scheduler', start_date+60, 120)
    schd2 = vm_ops.start_vm_scheduler(vm.get_vm().uuid, 'simple', 'simple_start_vm_scheduler', start_date+120, 120)
    test_stub.sleep_util(start_date+58)

    conditions = res_ops.gen_query_conditions('uuid', '=', schd1.uuid)
    schd1_state = res_ops.query_resource(res_ops.SCHEDULER, conditions)[0].state
    test_util.test_dsc('schd1_status: %s' % schd1_state)
    if schd1_state != 'Enabled':
         test_util.test_fail('check scheduler state, it is expected to be Enabled, but it is %s' % schd1_state)
   
    vm.destroy()

    conditions = res_ops.gen_query_conditions('uuid', '=', schd1.uuid)
    schd1_state = res_ops.query_resource(res_ops.SCHEDULER, conditions)[0].state
    test_util.test_dsc('after destroy vm schd1_status: %s' % schd1_state)
    if schd1_state != 'Disabled':
         test_util.test_fail('check scheduler state, it is expected to be Disabled, but it is %s' % schd1_state)  

    vm.recover()

    conditions = res_ops.gen_query_conditions('uuid', '=', schd1.uuid)
    schd1_state = res_ops.query_resource(res_ops.SCHEDULER, conditions)[0].state
    test_util.test_dsc('after recover vm schd1_status: %s' % schd1_state)
    if schd1_state != 'Enabled':
         test_util.test_fail('check scheduler state, it is expected to be Enabled, but it is %s' % schd1_state)
 
    schd_ops.delete_scheduler(schd1.uuid)
    schd_ops.delete_scheduler(schd2.uuid)
    vm.destroy()
    vm.set_delete_policy(delete_policy)
    test_util.test_pass('Check Scheduler State after DSuccess')

#Will be called only if exception happens in test().
def error_cleanup():
    global vm
    global schd1
    global schd2

    vm.set_delete_policy(delete_policy)
    if vm:
        vm.destroy()

    if schd1:
	schd_ops.delete_scheduler(schd1.uuid)

    if schd2:
	schd_ops.delete_scheduler(schd2.uuid)
