'''
New Perf Test for starting KVM VMs which were stopped.
The start number will depend on the environment variable: ZSTACK_TEST_NUM
This case's max thread is 1000

@author: Lei Liu
'''
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.test_lib as test_lib
from test_stub import *

class Start_VM_Parall(VM_Operation_Parall):

    def operate_vm_parall(self, vm_uuid):
        try:
            vm_ops.start_vm(vm_uuid, self.session_uuid)
        except:
            self.exc_info.append(sys.exc_info())

    def check_operation_result(self):
        for i in range(0, self.i):
            v1 = test_lib.lib_get_vm_by_uuid(self.vms[i].uuid)
            if v1.state != "Running":
                test_util.test_fail('Fail to start VM %s.' % v1.uuid)

def test():
    get_vm_con = res_ops.gen_query_conditions('state', '=', "Stopped")
    startvms = Start_VM_Parall(get_vm_con, "Running")
    startvms.parall_test_run()
    startvms.check_operation_result()
