'''

New Integration Test for License.

@author: Quarkonics  tianye
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.license_operations as lic_ops
import time
import datetime
import os
import base64

test_stub = test_lib.lib_get_test_stub()
#management_ip = os.environ.get('node1Ip')

def test():
    test_stub.reload_default_license()
    test_util.test_logger('Check default community license')
    test_stub.check_license(None, None, 2147483647, False, 'Community')

    test_util.test_logger('Load and Check Prepaid license with 1 day and 1 CPU')
    file_path = test_stub.gen_license('woodpecker', 'woodpecker@zstack.io', '1', 'Prepaid', '1', '')
    test_stub.load_license(file_path)
    issued_date = test_stub.get_license_info().issuedDate
    expired_date = test_stub.license_date_cal(issued_date, 86400 * 1)
    test_stub.check_license("woodpecker@zstack.io", 1, None, False, 'Paid', issued_date=issued_date, expired_date=expired_date)

    test_util.test_logger('update a  other MN_node license gen_other_license with 2 day 2 cpu')
    file_path = test_stub.gen_other_license('woodpecker', 'woodpecker@zstack.io', '2', 'Prepaid', '2', '')
    #file_path = "/home/test_err_license.txt"
    file_license1 = open(file_path.strip('\n')).read()
    file_license = base64.b64encode('%s' % file_license1)
    node_uuid = res_ops.query_resource(res_ops.MANAGEMENT_NODE)[0].uuid
    try:
        lic_ops.update_license(node_uuid, file_license)
    except Exception:
        pass

    issued_date = test_stub.get_license_info().issuedDate
    expired_date = test_stub.license_date_cal(issued_date, 86400 * 1)
    test_stub.check_license("woodpecker@zstack.io", 1, None, False, 'Paid', issued_date=issued_date, expired_date=expired_date)

    test_util.test_logger('Update License and Check Trial license with 5 day and 10 HOST')
    file_path = test_stub.gen_license('woodpecker', 'woodpecker@zstack.io', '5', 'Prepaid', '', '10')
    file_license1 = open(file_path.strip('\n')).read()
    file_license = base64.b64encode('%s' % file_license1)
    node_uuid = res_ops.query_resource(res_ops.MANAGEMENT_NODE)[0].uuid
    lic_ops.update_license(node_uuid, file_license)
    issued_date = test_stub.get_license_info().issuedDate
    expired_date = test_stub.license_date_cal(issued_date, 86400 * 5)
    test_stub.check_license("woodpecker@zstack.io", None, 10, False, 'Paid', issued_date=issued_date, expired_date=expired_date)

    test_util.test_pass('Check License Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
