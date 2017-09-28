'''

New Integration Test for hybrid.

@author: Legion
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib


test_stub = test_lib.lib_get_test_stub()
hybrid = test_stub.HybridObject()
name = 'vpn-gateway-%s' % test_stub._postfix
description = 'vpn-gateway-for-test-%s' % test_stub._postfix

def test():
    hybrid.add_datacenter_iz(check_vpn_gateway=True)
    hybrid.update_vpn_gateway(name=name)
    hybrid.update_vpn_gateway(description=description)
    test_util.test_pass('Update Vpc Vpn Gateway Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)
