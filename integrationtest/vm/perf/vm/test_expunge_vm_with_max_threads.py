'''
New Perf Test for expunging KVM VMs which were deleted.
The expunged number will depend on the environment variable: ZSTACK_TEST_NUM.
This case's max thread is 1000.
Before run this test, at least 1 VM is created, and at least 1 VM was destoryed.

@author: Liu Lei
'''

import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
from test_stub import *

class Expunge_VM_Parall(VM_Operation_Parall):

    def operate_vm_parall(self, vm_uuid):
        try:
            vm_ops.expunge_vm(vm_uuid, self.session_uuid)
        except:
            self.exc_info.append(sys.exc_info())

    def check_operation_result(self):
        for i in range(0, self.i):
            v1 = test_lib.lib_get_vm_by_uuid(self.vms[i].uuid)
            if v1 is not None:
                test_util.test_fail('Fail to expunge VM %s.' % v1.uuid)

def test():
    get_vm_con = res_ops.gen_query_conditions('state', '=', "Destroyed")
    expungevms = Expunge_VM_Parall(get_vm_con, "Running")
    expungevms.parall_test_run()
    expungevms.check_operation_result()
