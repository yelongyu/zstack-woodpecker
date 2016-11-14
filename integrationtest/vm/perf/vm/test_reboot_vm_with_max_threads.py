'''
New Perf Test for rebooting KVM VMs.
The rebooted number will depend on the environment variable: ZSTACK_TEST_NUM
This case's max thread is 1000

@author: Liu Lei
'''

import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import time
from test_stub import *

class Reboot_VM_Parall(VM_Operation_Parall):

    def operate_vm_parall(self, vm_uuid):
        try:
            vm_ops.reboot_vm(vm_uuid, self.session_uuid)
            v1 = test_lib.lib_get_vm_by_uuid(vm_uuid)
            if v1.state == "Rebooting":
                test_util.test_fail('Fail to reboot VM %s.' % v1.uuid)

        except:
            self.exc_info.append(sys.exc_info())

def test():
    get_vm_con = res_ops.gen_query_conditions('state', '=', "Running")
    rebootvms = Reboot_VM_Parall(get_vm_con, "Running")
    rebootvms.parall_test_run()
