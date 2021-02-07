'''

New Integration Test for hybrid.

@author: Legion
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state


test_obj_dict = test_state.TestStateDict()
test_stub = test_lib.lib_get_test_stub()
hybrid = test_stub.HybridObject()
name = 'aliyun-vbr-%s' % test_stub._postfix
description = 'test-aliyun-vbr-%s' % test_stub._postfix

def test():
    hybrid.add_datacenter_iz(region_id='cn-shanghai', ks2=True)
    hybrid.sync_vbr()
    hybrid.update_vbr(name=name)
    hybrid.update_vbr(description=description)
    hybrid.update_vbr()
    test_util.test_pass('Update Virtual Border Router Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)
