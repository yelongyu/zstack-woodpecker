'''
New Perf Test for rebooting KVM VMs which were stopped.
The reboot number will depend on the environment variable: ZSTACK_TEST_NUM
This case's max thread is 1000

@author: Carl
'''

import os
import time
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.test_lib as test_lib
from test_stub import *

global reboot_date
global vm_stat_flag

class Reboot_VM_Simple_Scheduler_Parall(VM_Operation_Parall):
    date=int(time.time())
    def operate_vm_parall(self, vm_uuid):
        try:
            vm_ops.reboot_vm_scheduler(vm_uuid, 'simple', 'simple_reboot_vm_scheduler', 0, 1, 1)
        except:
            self.exc_info.append(sys.exc_info())

    def check_operation_result(self):
        time.sleep(30)
        start_msg_mismatch = 1
        for k in range(0, 100):
            for i in range(0, self.i):
                vm_stat_flag=0
                if not test_lib.lib_find_in_local_management_server_log(self.date+k, '[msg send]: {"org.zstack.header.vm.RebootVmInstanceMsg', self.vms[i].uuid):
                    test_util.test_warn('RebootVmInstanceMsg is expected to execute at %s' % (self.date+k))
                    vm_stat_flag=1
                start_msg_mismatch += 1
            if vm_stat_flag == 0:
                break
        if start_msg_mismatch > 1000:
            test_util.test_fail('%s of 1000 RebootVmInstanceMsg not executed at expected timestamp' % (start_msg_mismatch))

def test():
    get_vm_con = res_ops.gen_query_conditions('state', '=', "Running")
    rebootvms = Reboot_VM_Simple_Scheduler_Parall(get_vm_con, "Running")
    rebootvms.parall_test_run()
    rebootvms.check_operation_result()
