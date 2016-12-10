'''
New Perf Test for expunging KVM VMs which were deleted.
The expunged number will depend on the environment variable: ZSTACK_TEST_NUM.
This case's max thread is 1000.
Before run this test, at least 1 VM is created, and at least 1 VM was destoryed.

@author: Carl
'''

import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.account_operations as acc_ops
from test_stub import *
import random
import string 

new_account_uuid = None
global new_account

random_name=''.join(random.sample(string.ascii_letters + string.digits, 8))

new_account = acc_ops.create_account(random_name, 'password', 'Normal')
new_account_uuid = new_account.uuid

class Change_VM_Owner_Parall(VM_Operation_Parall):
    def operate_vm_parall(self, vm_uuid):
        try:
            res_ops.change_recource_owner(new_account.uuid,vm_uuid)
        except:
            self.exc_info.append(sys.exc_info())
    def check_operation_result(self):
        for i in range(0, self.i):
            real_account_uuid=res_ops.get_resource_owner(self.vms[i].uuid.split(';'))
            #real_account.uuid=real_account.uuid
            if  cmp(new_account.uuid,real_account_uuid):
                test_util.test_fail('Fail to change VM owner %s.' % self.vms[i].uuid)

def test():
    get_vm_con = res_ops.gen_query_conditions('state', '!=', "Destroyed")
    changeownervms = Change_VM_Owner_Parall(get_vm_con,"")
    changeownervms.parall_test_run()
    changeownervms.check_operation_result()

def error_cleanup():
    global new_account_uuid
    if new_account:
        account_operations.delete_account(new_account.uuid)

