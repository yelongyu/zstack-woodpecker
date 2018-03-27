'''

New Simulator Test for Long Job

@author: Legion
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import time

test_obj_dict = test_state.TestStateDict()
test_stub = test_lib.lib_get_test_stub()
longjob = test_stub.Longjob()

def test():
    longjob.add_image()
    time.sleep(10)
    longjob.delete_image()
    test_util.test_pass('Add Image Longjob Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)
