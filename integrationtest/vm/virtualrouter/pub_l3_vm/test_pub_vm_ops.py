'''

@author: FangSun
'''


import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state

import os


test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()


def test():
    pub_l3_vm, flat_l3_vm, vr_l3_vm = test_stub.generate_pub_test_vm(tbj=test_obj_dict)

    for vm in (pub_l3_vm, flat_l3_vm, vr_l3_vm):
        for action in ('stop', 'start', 'reboot', 'suspend', 'resume'):
            getattr(vm, action)()

    test_lib.lib_error_cleanup(test_obj_dict)


def env_recover():
    test_lib.lib_error_cleanup(test_obj_dict)

