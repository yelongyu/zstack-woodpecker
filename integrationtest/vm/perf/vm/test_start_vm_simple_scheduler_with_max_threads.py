'''
New Perf Test for starting KVM VMs which were stopped.
The start number will depend on the environment variable: ZSTACK_TEST_NUM
This case's max thread is 1000

@author: Carl
'''

import os
import time
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.test_lib as test_lib
from test_stub import *

global start_date
global vm_stat_flag

class Start_VM_Simple_Scheduler_Parall(VM_Operation_Parall):
    date=int(time.time())
    def operate_vm_parall(self, vm_uuid):
        try:
            vm_ops.start_vm_scheduler(vm_uuid, 'simple', 'simple_start_vm_scheduler', 0, 1, 1)
        except:
            self.exc_info.append(sys.exc_info())

    def check_operation_result(self):
        for x in range(30): 
            start_msg_mismatch=1
            time.sleep(10)
            for i in range(0, self.i):
                vm_stat_flag=0
                v1 = test_lib.lib_get_vm_by_uuid(self.vms[i].uuid)
                if v1.state != "Running":
                    start_msg_mismatch += 1
                    vm_stat_flag=1
            if vm_stat_flag == 0:
                break
            if start_msg_mismatch > 30:
                test_util.test_fail('StartVmInstance scheduler doesn\'t work as expected')



def test():
    get_vm_con = res_ops.gen_query_conditions('state', '=', "Stopped")
    startvms = Start_VM_Simple_Scheduler_Parall(get_vm_con, "Stopped")
    start_date=int(time.time())
    startvms.parall_test_run()
    startvms.check_operation_result()
