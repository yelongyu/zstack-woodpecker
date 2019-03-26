'''

New Integration Test for multiple shared primary storage

@author: Legion
'''

import os
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib

test_obj_dict = test_state.TestStateDict()
test_stub = test_lib.lib_get_test_stub()
multi_ps = test_stub.MultiSharedPS()

case_flavor = dict(shared1root_shared2data = dict(shared1='root', shared2='data'),
                   shared1data_shared2root = dict(shared1='data', shared2='root')
                   )

def test():
    flavor = case_flavor[os.getenv('CASE_FLAVOR')]
    if flavor['shared1'] == 'data':
        multi_ps.create_vm(with_data_vol=True, reverse=True)
    else:
        multi_ps.create_vm(with_data_vol=True)

    multi_ps.check_vol_seperated()
    test_util.test_pass('Create VM with Volume Seperated Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    if multi_ps.vm:
        try:
            for vm in multi_ps.vm:
                vm.destroy()
        except:
            pass
