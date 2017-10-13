'''
@author: FangSun
'''
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import functools

_config_ = {
        'timeout' : 1000,
        'noparallel' : True
        }

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

'''
def test()
This document sting is a dirty solution to find test case
'''

test = functools.partial(test_stub.vm_offering_testcase,
                         tbj=test_obj_dict,
                         test_image_name="imageName_i_u12",
                         add_cpu=True,
                         add_memory=False,
                         need_online=True)

test = test_lib.deprecated_case(test)

def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
