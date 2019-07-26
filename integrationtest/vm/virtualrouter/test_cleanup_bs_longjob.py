'''

New Integration Test for Long Job

@author: Legion
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import apibinding.inventory as inventory
import zstackwoodpecker.operations.resource_operations as res_ops
import time

test_obj_dict = test_state.TestStateDict()
test_stub = test_lib.lib_get_test_stub()
longjob = test_stub.Longjob()

def test():
    bs = res_ops.query_resource(res_ops.BACKUP_STORAGE)
    for i in bs:
        if i.type == inventory.IMAGE_STORE_BACKUP_STORAGE_TYPE:
            break
    else:
        test_util.test_logger('The BS type is: %s.' % i.type)
        test_util.test_skip('Skip test on non-imagestore')
    longjob.add_image(img_url='file:///opt/zstack-dvd/zstack-image-1.4.qcow2', bs='ImageStore')
    time.sleep(10)
    longjob.delete_image()
    longjob.expunge_image()
    longjob.cleanup_bs()
    test_util.test_pass('Clean up BackupStorage Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)
