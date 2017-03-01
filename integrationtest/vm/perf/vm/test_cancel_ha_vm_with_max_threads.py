'''
New Perf Test for expunging KVM VMs which were deleted.
The cancel_had number will depend on the environment variable: ZSTACK_TEST_NUM.
This case's max thread is 1000.
Before run this test, at least 1 VM is created, and at least 1 VM was destoryed.

@author: Carl
'''

import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.ha_operations as ha_ops
from test_stub import *

class Cancel_HA_VM_Parall(VM_Operation_Parall):

    def operate_vm_parall(self, vm_uuid):
        try:
            ha_ops.del_vm_instance_ha_level(vm_uuid)
        except:
            self.exc_info.append(sys.exc_info())

def test():
    get_vm_con = res_ops.gen_query_conditions('state', '!=', "Destroyed")
    cancel_ha_vms = Cancel_HA_VM_Parall(get_vm_con, "Running")
    cancel_ha_vms.parall_test_run()
