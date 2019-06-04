'''

New Integration Test for Long Job

@author: Legion
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import apibinding.inventory as inventory

test_obj_dict = test_state.TestStateDict()
test_stub = test_lib.lib_get_test_stub()
longjob = test_stub.Longjob()

def test():
    vm = longjob.create_vm()

    test_obj_dict.add_vm(longjob.vm)
    bss = res_ops.query_resource(res_ops.BACKUP_STORAGE)
    for bs in bss:
        if bs.type == inventory.SFTP_BACKUP_STORAGE_TYPE:
            longjob.vm.stop()
            break
    longjob.crt_vm_image()

    test_lib.lib_robot_cleanup(test_obj_dict)
    longjob.delete_image()
    test_util.test_pass('Root Volume Create Image Longjob Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)
