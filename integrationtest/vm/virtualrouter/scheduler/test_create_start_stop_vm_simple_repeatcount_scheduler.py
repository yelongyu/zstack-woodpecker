'''

New Integration Test for Simple VM stop/start scheduler with repeatCount.

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
schd_job1 = None
schd_job2 = None
schd_trigger1 = None
schd_trigger2 = None


def test():
    global vm
    global schd_job1
    global schd_job2
    global schd_trigger1
    global schd_trigger2

    vm = test_stub.create_vlan_vm(os.environ.get('l3VlanNetworkName1'))
    start_date = int(time.time())
    schd_job1 = schd_ops.create_scheduler_job('simple_stop_vm_scheduler', 'simple_stop_vm_scheduler', vm.get_vm().uuid, 'stopVm', None)
    schd_trigger1 = schd_ops.create_scheduler_trigger('simple_stop_vm_scheduler', start_date+60, 3, 120, 'simple')
    schd_ops.add_scheduler_job_to_trigger(schd_trigger1.uuid, schd_job1.uuid)
    #schd1 = vm_ops.stop_vm_scheduler(vm.get_vm().uuid, 'simple', 'simple_stop_vm_scheduler', start_date+60, 120, 3)
#    if schd1.stopTime != start_date + 60 + 120 * 3:
#        test_util.test_fail('[scheduler:] %s is expected have stopTime as %s' % (schd1.uuid, start_date + 60 + 120 * 3))
    schd_job2 = schd_ops.create_scheduler_job('simple_start_vm_scheduler', 'simple_start_vm_scheduler', vm.get_vm().uuid, 'startVm', None)
    schd_trigger2 = schd_ops.create_scheduler_trigger('simple_start_vm_scheduler', start_date+120, 2, 120, 'simple')
    schd_ops.add_scheduler_job_to_trigger(schd_trigger2.uuid, schd_job2.uuid)
    #schd2 = vm_ops.start_vm_scheduler(vm.get_vm().uuid, 'simple', 'simple_start_vm_scheduler', start_date+120, 120, 2)
#    if schd2.stopTime != start_date + 120 + 120 * 2:
#        test_util.test_fail('[scheduler:] %s is expected have stopTime as %s' % (schd2.uuid, start_date + 120 + 120 * 2))

    test_stub.sleep_util(start_date+58)
    vm.update()
    if not test_lib.lib_is_vm_running(vm.get_vm()):
        test_util.test_fail('VM is expected to run until stop vm scheduler start_date')

    for i in range(0, 5):
        test_util.test_logger('round %s' % (i))
        test_stub.sleep_util(start_date + 60 + 120*i + 5)
        test_util.test_logger('check VM status at %s, VM is expected to stop' % (start_date + 60 + 120*i + 5))
        vm.update()
        if vm.get_vm().state != 'Stopping' and vm.get_vm().state != 'Stopped':
            test_util.test_fail('VM is expected to stop')

        test_stub.sleep_util(start_date + 60 + 120*i + 65)
	if i >= 2:
            test_util.test_logger('check VM status at %s, VM is expected to stay stopped' % (start_date + 60 + 120*i + 65))
            vm.update()
	    if vm.get_vm().state != 'Stopped':
                test_util.test_fail('VM is expected to stay stop')
	    continue

        test_util.test_logger('check VM status at %s, VM is expected to start' % (start_date + 60 + 120*i + 65))
        vm.update()
        if vm.get_vm().state != 'Starting' and vm.get_vm().state != 'Running':
            test_util.test_fail('VM is expected to start')

    schd_ops.del_scheduler_job(schd_job1.uuid)
    schd_ops.del_scheduler_trigger(schd_trigger1.uuid)
    schd_ops.del_scheduler_job(schd_job2.uuid)
    schd_ops.del_scheduler_trigger(schd_trigger2.uuid)

    vm.destroy()
    test_util.test_pass('Create Simple VM Stop Start Scheduler Repeat Count Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global vm
    global schd_job1
    global schd_job2
    global schd_trigger1
    global schd_trigger2

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

