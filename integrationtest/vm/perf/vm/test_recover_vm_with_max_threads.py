'''
New Perf Test for recovering KVM VMs.
The recovered number will depend on the environment variable: ZSTACK_TEST_NUM.
This case's max thread is 1000.
Before run this test, at least 1 VM is created and at least 1 VM's status was destoryed.

@author: Lei Liu
'''

import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
from test_stub import *

class Recover_VM_Parall(VM_Operation_Parall):
    def operate_vm_parall(self, vm_uuid):
        try:
            vm_ops.recover_vm(vm_uuid, self.session_uuid)
        except:
            self.exc_info.append(sys.exc_info())

def test():
    get_vm_con = res_ops.gen_query_conditions('state', '=', "Destroyed")
    recovervms = Recover_VM_Parall(get_vm_con, "Destroyed")
    recovervms.parall_test_run()
    recovervms.check_operation_result()


