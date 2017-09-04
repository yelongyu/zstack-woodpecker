'''
@author: FangSun
'''

import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state

_config_ = {
        'timeout' : 1000,
        'noparallel' : True
        }


test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()


test = test_stub.vmoffering_testcase_maker(tbj=test_obj_dict,
                                           test_image_name="imageName_i_c7",
                                           add_cpu=True,
                                           add_memory=False,
                                           need_online=False)


def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
