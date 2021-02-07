'''

New Integration Test for multiple shared primary storage in one cluster

@author: Legion
'''

import os
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib

test_obj_dict = test_state.TestStateDict()
test_stub = test_lib.lib_get_test_stub()
multi_ps = test_stub.MultiSharedPS()

case_flavor = dict(from_shared1_to_shared2 = dict(shared1=True, shared2=False),
                   from_shared2_to_shared1 = dict(shared1=False, shared2=True)
                   )

def test():
    flavor = case_flavor[os.getenv('CASE_FLAVOR')]
    if flavor['shared1']:
        multi_ps.create_vm(l3_name=os.getenv('l3PublicNetworkName'), reverse=True)
        multi_ps.copy_data(multi_ps.vm[0])
        multi_ps.create_image(multi_ps.vm[0])
        multi_ps.create_vm(image_name=multi_ps.image.name)
        multi_ps.check_data(multi_ps.vm[1])
    else:
        multi_ps.create_vm(l3_name=os.getenv('l3PublicNetworkName'))
        multi_ps.copy_data(multi_ps.vm[0])
        multi_ps.create_image(multi_ps.vm[0])
        multi_ps.create_vm(image_name=multi_ps.image.name, reverse=True)
        multi_ps.check_data(multi_ps.vm[1])
    test_util.test_pass('Migrate VM among different type of PS Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    if multi_ps.vm:
        try:
            for vm in multi_ps.vm:
                vm.destroy()
        except:
            pass
