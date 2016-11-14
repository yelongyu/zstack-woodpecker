'''
New Perf Test for stopping KVM VMs which are running.
The stopped number will depend on the environment variable: ZSTACK_TEST_NUM.
This case's max thread is 1000.
Before run this test, at least 1 VM is created and at least 1 VM's status is Starting.

@author: Liu Lei
'''

import zstackwoodpecker.operations.resource_operations as res_ops
import time
from test_stub import VM_Operation_Parall

def test():
    get_vm_con = res_ops.gen_query_conditions('state', '=', "Running")
    stopvms = VM_Operation_Parall(get_vm_con, "Running")
    stopvms.parall_test_run()
    stopvms.check_operation_result()
