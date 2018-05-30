'''

New Integration Test for License.

@author: yetian
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.license_operations as lic_ops
import time
import datetime
import os

test_stub = test_lib.lib_get_test_stub()

def test():
    test_stub.reload_default_license()
    test_util.test_logger('Check default community license')
    test_stub.check_license(None, None, 2147483647, False, 'Community')

    test_util.test_logger('load and check addon license project-management with 2 day ')
    file_path = test_stub.gen_addons_license('woodpecker', 'woodpecker@zstack.io', '2', 'Addon', '', '', 'project-management')
    test_stub.load_license(file_path)
    issued_date = test_stub.get_license_addons_info().issuedDate
    expired_date = test_stub.license_date_cal(issued_date, 86400 * 2)
    test_stub.check_license_addons("woodpecker@zstack.io", None, 2147483647, False, 'AddOn', issued_date=issued_date, expired_date=expired_date)

    test_util.test_logger('Load and Check Hybrid license with 2 day and 1 HOST')
    file_path = test_stub.gen_license('woodpecker', 'woodpecker@zstack.io', '2', 'Hybrid', '', '1')
    test_stub.load_license(file_path)
    issued_date = test_stub.get_license_info().issuedDate
    expired_date = test_stub.license_date_cal(issued_date, 86400 * 2)
    test_stub.check_license("woodpecker@zstack.io", None, 1, False, 'Hybrid', issued_date=issued_date, expired_date=expired_date)

    test_util.test_logger('load and check addon license project-management with 1 day ')
    file_path = test_stub.gen_addons_license('woodpecker', 'woodpecker@zstack.io', '1', 'Addon', '', '', 'project-management')
    test_stub.load_license(file_path)
    issued_date = test_stub.get_license_addons_info().issuedDate
    expired_date = test_stub.license_date_cal(issued_date, 86400 * 1)
    test_stub.check_license_addons("woodpecker@zstack.io", None, 1, False, 'AddOn', issued_date=issued_date, expired_date=expired_date)

    test_util.test_logger('Load and Check Prepaid license with 1 day and 1 CPU')
    file_path = test_stub.gen_license('woodpecker', 'woodpecker@zstack.io', '1', 'Prepaid', '1', '')
    test_stub.load_license(file_path)
    issued_date = test_stub.get_license_info().issuedDate
    expired_date = test_stub.license_date_cal(issued_date, 86400 * 1)
    test_stub.check_license("woodpecker@zstack.io", 1, None, False, 'Prepaid', issued_date=issued_date, expired_date=expired_date)

    test_util.test_logger('load and check addon license project-management with 3 day ')
    file_path = test_stub.gen_addons_license('woodpecker', 'woodpecker@zstack.io', '1', 'Addon', '', '', 'project-management')
    test_stub.load_license(file_path)
    issued_date = test_stub.get_license_addons_info().issuedDate
    expired_date = test_stub.license_date_cal(issued_date, 86400 * 3)
    test_stub.check_license_addons("woodpecker@zstack.io", None, 3, False, 'AddOn', issued_date=issued_date, expired_date=expired_date)

    test_util.test_logger('Load and Check Hybrid license with 2 day and 10 HOST')
    file_path = test_stub.gen_license('woodpecker', 'woodpecker@zstack.io', '2', 'Hybrid', '', '10')
    test_stub.load_license(file_path)
    issued_date = test_stub.get_license_info().issuedDate
    expired_date = test_stub.license_date_cal(issued_date, 86400 * 2)
    test_stub.check_license("woodpecker@zstack.io", None, 10, False, 'Hybrid', issued_date=issued_date, expired_date=expired_date)

    test_util.test_logger('load and check addon license project-management with 10 day ')
    file_path = test_stub.gen_addons_license('woodpecker', 'woodpecker@zstack.io', '1', 'Addon', '', '', 'project-management')
    test_stub.load_license(file_path)
    issued_date = test_stub.get_license_addons_info().issuedDate
    expired_date = test_stub.license_date_cal(issued_date, 86400 * 10)
    test_stub.check_license_addons("woodpecker@zstack.io", None, 10, False, 'AddOn', issued_date=issued_date, expired_date=expired_date)

    test_util.test_logger('Load and Check Trial license with 1 HOST')
    file_path = test_stub.gen_license('woodpecker', 'woodpecker@zstack.io', '1', 'Trial', '', '1')
    test_stub.load_license(file_path)
    test_stub.check_license('woodpecker@zstack.io', None, 1, False, 'Trial')

    test_util.test_logger('load and check addon license project-management with 3 day ')
    file_path = test_stub.gen_addons_license('woodpecker', 'woodpecker@zstack.io', '1', 'Addon', '', '', 'project-management')
    test_stub.load_license(file_path)
    issued_date = test_stub.get_license_addons_info().issuedDate
    expired_date = test_stub.license_date_cal(issued_date, 86400 * 3)
    test_stub.check_license_addons("woodpecker@zstack.io", None, 3, False, 'AddOn', issued_date=issued_date, expired_date=expired_date)

    test_util.test_logger('Load and Check Hybrid license with 3 day and 2 HOST')
    file_path = test_stub.gen_license('woodpecker', 'woodpecker@zstack.io', '3', 'Hybrid', '', '1')
    test_stub.load_license(file_path)
    issued_date = test_stub.get_license_info().issuedDate
    expired_date = test_stub.license_date_cal(issued_date, 86400 * 3)
    test_stub.check_license("woodpecker@zstack.io", None, 1, False, 'Hybrid', issued_date=issued_date, expired_date=expired_date)

    test_util.test_logger('load and check addon license project-management with 3 day ')
    file_path = test_stub.gen_addons_license('woodpecker', 'woodpecker@zstack.io', '1', 'Addon', '', '', 'project-management')
    test_stub.load_license(file_path)
    issued_date = test_stub.get_license_addons_info().issuedDate
    expired_date = test_stub.license_date_cal(issued_date, 86400 * 3)
    test_stub.check_license_addons("woodpecker@zstack.io", None, 3, False, 'AddOn', issued_date=issued_date, expired_date=expired_date)

    test_util.test_pass('Check License Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
