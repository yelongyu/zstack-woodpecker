'''

Integration Test for scheduler reboot VM in HA mode.

@author: Quarkonics
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.zstack_test.zstack_test_vm as test_vm_header
import zstackwoodpecker.operations.vm_operations as vm_ops
import zstackwoodpecker.operations.scheduler_operations as schd_ops
import test_stub
import time
import os

vm = None
node1_ip = None
node2_ip = None

def test():
    global vm
    global node1_ip
    vm = test_stub.create_basic_vm()
    vm.check()

    start_date = int(time.time())
    schd = vm_ops.reboot_vm_scheduler(vm.get_vm().uuid, 'simple', 'simple_reboot_vm_scheduler', start_date+60, 30)

    node1_ip = os.environ.get('node1Ip')
    node2_ip = os.environ.get('node2Ip')
    test_util.test_logger("shutdown node: %s" % (node1_ip))
    cmd = "init 0"
    host_username = os.environ.get('nodeUserName')
    host_password = os.environ.get('nodePassword')
    rsp = test_lib.lib_execute_ssh_cmd(node1_ip, host_username, host_password, cmd, 180)
    test_util.test_logger("wait for 2 minutes to see if http api still works well")
    time.sleep(180)
    test_stub.exercise_connection(600)
    time.sleep(180)

    scheduler_execution_count = 0
    for i in range(0, 30):
        for j in range(0, 6):
            if test_lib.lib_find_in_remote_management_server_log(node1_ip, host_username, host_password, start_date+60+30*i+j, '[msg received]: {"org.zstack.header.vm.RebootVmInstanceMsg', vm.get_vm().uuid):
                scheduler_execution_count += 1
            if test_lib.lib_find_in_remote_management_server_log(node2_ip, host_username, host_password, start_date+60+30*i+j, '[msg received]: {"org.zstack.header.vm.RebootVmInstanceMsg', vm.get_vm().uuid):
                scheduler_execution_count -= 1

    if abs(scheduler_execution_count) < 5:
            test_util.test_fail('VM reboot scheduler is expected to executed for more than 5 times, while it only execute %s times' % (scheduler_execution_count))
    schd_ops.delete_scheduler(schd.uuid)
    vm.destroy()

    test_util.test_logger("recover node: %s" % (node1_ip))
    os.system('bash -ex %s %s' % (os.environ.get('nodeRecoverScript'), node1_ip))
    time.sleep(180)
    test_stub.exercise_connection(600)

    test_util.test_pass('Scheduler Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global vm
    global node1_ip
    if vm:
        try:
            vm.destroy()
        except:
            pass
    test_util.test_logger("recover node: %s" % (node1_ip))
    os.system('bash -ex %s %s' % (os.environ.get('nodeRecoverScript'), node1_ip))
    time.sleep(180)
    test_stub.exercise_connection(600)
