'''

New Integration Test for License.

@author: ye.tian 20181005
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.license_operations as lic_ops
import time
import datetime
import os

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
def test():
    test_stub.reload_default_license()
    test_util.test_logger('Check default community license')
    test_stub.check_license(None, None, 2147483647, False, 'Community')

    test_util.test_logger('Load and Check TrialExt license with 5 day and 5 HOST')
    file_path = test_stub.gen_license('woodpecker', 'woodpecker@zstack.io', '20', 'HybridTrialExt', '', '5')
    test_stub.load_license(file_path)
    issued_date = test_stub.get_license_info().issuedDate
    expired_date = test_stub.license_date_cal(issued_date, 86400 * 20)
    test_stub.check_license("woodpecker@zstack.io", None, 5, False, 'HybridTrialExt', issued_date=issued_date, expired_date=expired_date)

    node_uuid = res_ops.query_resource(res_ops.MANAGEMENT_NODE)[0].uuid
    test_util.test_logger('start to delete the license')
    uuid = test_stub.get_license_info().uuid
    lic_ops.delete_license(node_uuid, uuid)
    test_util.test_logger('delete the license [uuid:] %s' % uuid)

    test_util.test_pass('Check License Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
