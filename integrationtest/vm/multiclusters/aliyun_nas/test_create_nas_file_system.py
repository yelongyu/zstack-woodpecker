'''

New Integration Test for AliyunNAS.

@author: Legion
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state


test_obj_dict = test_state.TestStateDict()
test_stub = test_lib.lib_get_test_stub()
nas = test_stub.AliyunNAS()

def test():
    nas.crt_nas_fs()
    nas.del_nas_fs()
    test_util.test_pass('Create/Delete NAS File System Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)
