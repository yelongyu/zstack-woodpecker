'''

New Integration Test for License addons vmware.

@author: yetian
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

def test():
    test_util.test_logger('Load and Check Prepaid license with 1 day and 1 CPU')
    file_path = test_stub.gen_license('woodpecker', 'woodpecker@zstack.io', '1', 'Prepaid', '1', '')
    test_stub.load_license(file_path)
    issued_date = test_stub.get_license_info().issuedDate
    expired_date = test_stub.license_date_cal(issued_date, 86400 * 1)
    test_stub.check_license("woodpecker@zstack.io", 1, None, False, 'Paid', issued_date=issued_date, expired_date=expired_date)

    test_util.test_logger('load and check addon license vmware with 2 day and 2 CPU ')
    file_path = test_stub.gen_addons_license('woodpecker', 'woodpecker@zstack.io', '2', 'Addon', '2', '', 'vmware')
    node_uuid = res_ops.query_resource(res_ops.MANAGEMENT_NODE)[0].uuid
    test_stub.update_license(node_uuid, file_path)
    issued_date = test_stub.get_license_addons_info().issuedDate
    expired_date = test_stub.license_date_cal(issued_date, 86400 * 2)
    test_stub.check_license_addons(2, None, False, 'AddOn', issued_date=issued_date, expired_date=expired_date)

    test_util.test_logger('load and check addon license vmware with 10 day and 5 CPU ')
    file_path = test_stub.gen_addons_license('woodpecker', 'woodpecker@zstack.io', '10', 'Addon', '5', '', 'project-management')
    with open(file_path.strip('\n'), 'r') as file_license2:
        file_license1 = file_license2.read()
        file_license = base64.b64encode('%s' % file_license1)
    node_uuid = res_ops.query_resource(res_ops.MANAGEMENT_NODE)[0].uuid
    #test_stub.update_license(node_uuid, file_path)
    lic_ops.update_license(node_uuid, file_license)
    issued_date = test_stub.get_license_addons_info().issuedDate
    expired_date = test_stub.license_date_cal(issued_date, 86400 * 10)
    test_stub.check_license_addons(5, None, False, 'AddOn', issued_date=issued_date, expired_date=expired_date)

    test_util.test_logger('Load and Check Hybrid license with 20 day and 10 CPU')
    file_path = test_stub.gen_license('woodpecker', 'woodpecker@zstack.io', '10', 'Hybrid', '10', '')
    test_stub.load_license(file_path)
    issued_date = test_stub.get_license_info().issuedDate
    expired_date = test_stub.license_date_cal(issued_date, 86400 * 20)
    test_stub.check_license("woodpecker@zstack.io", 10, None, False, 'Hybrid', issued_date=issued_date, expired_date=expired_date)

    test_util.test_pass('Check License Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
