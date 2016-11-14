'''
New Perf Test for destroying KVM VMs which are running.
The destroyed number will depend on the environment variable: ZSTACK_TEST_NUM
This case's max thread is 1000
Before run this test, at least 1 VM is created.

@author: Liu Lei
'''

import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
from test_stub import *

class Destroy_VM_Parall(VM_Operation_Parall):
    def operate_vm_parall(self, vm_uuid):
        try:
            vm_ops.destroy_vm(vm_uuid, self.session_uuid)
        except:
            self.exc_info.append(sys.exc_info())

    def check_operation_result(self):
        for i in range(0, self.i):
            v1 = test_lib.lib_get_vm_by_uuid(self.vms[i].uuid)
            if v1.state != "Destroyed":
                test_util.test_fail('Fail to destroy VM %s.' % v1.uuid)

def test():
    get_vm_con = res_ops.gen_query_conditions('state', '!=', "Destroyed")
    destroyvms = Destroy_VM_Parall(get_vm_con, "Running")
    destroyvms.parall_test_run()
    destroyvms.check_operation_result()

