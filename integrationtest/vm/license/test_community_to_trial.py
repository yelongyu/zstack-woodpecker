'''

New Integration Test for License.

@author: Quarkonics
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.license_operations as lic_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import time
import os

test_stub = test_lib.lib_get_test_stub()

def test():
    test_stub.reload_default_license()
    test_util.test_logger('Check default community license')
    test_stub.check_license(None, None, 2147483647, False, 'Community')

    test_util.test_logger('Load and Check Trial license with 1 HOST')
    file_path = test_stub.gen_license('woodpecker', 'woodpecker@zstack.io', '1', 'Trial', '', '1')
    test_stub.load_license(file_path)
    test_stub.check_license('woodpecker@zstack.io', None, 1, False, 'Trial')

    node_uuid = res_ops.query_resource(res_ops.MANAGEMENT_NODE)[0].uuid
    test_util.test_logger('start to delete the license')
    uuid = test_stub.get_license_info().uuid
    lic_ops.delete_license(node_uuid, uuid)
    test_util.test_logger('delete the license [uuid:] %s' % uuid)

    test_util.test_pass('Check License Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
