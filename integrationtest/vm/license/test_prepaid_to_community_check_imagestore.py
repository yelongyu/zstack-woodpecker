'''

New Integration Test for License.

@author: Quarkonics
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.license_operations as lic_ops
import zstackwoodpecker.operations.zone_operations as zone_ops
import zstackwoodpecker.operations.backupstorage_operations as bs_ops
import zstackwoodpecker.operations.image_operations as img_ops
import time
import datetime
import os
import zstackwoodpecker.operations.resource_operations as res_ops

test_stub = test_lib.lib_get_test_stub()
node_ip = os.environ.get('node1Ip')
nodepassword = os.environ.get('nodePassword')
nodeUserName = os.environ.get('nodeUserName')

def test():

    file_path = test_stub.gen_license('woodpecker', 'woodpecker@zstack.io', '1', 'Prepaid', '1', '')
    test_stub.load_license(file_path)
    issued_date = test_stub.get_license_info().issuedDate
    expired_date = test_stub.license_date_cal(issued_date, 86400 * 1)
    test_stub.check_license("woodpecker@zstack.io", 1, None, False, 'Paid', issued_date=issued_date, expired_date=expired_date)

    test_util.test_logger('create zone and add the bs of the imagestore')
    node_uuid = res_ops.query_resource(res_ops.MANAGEMENT_NODE)[0].uuid
    test_stub.create_zone(zone_name)
    zone_uuid = res_ops.query_resource(res_ops.ZONE)[0].uuid
    print zone_uuid    

    bs_username = os.environ.get('node1Ip')
    bs_username = os.environ.get('nodeUserName')
    bs_password = os.environ.get('nodePassword')
    test_stub.create_image_store_backup_storage(bs_name, bs_hostname, bs_username, bs_password, bs_url, bs_sshport)
    bs_uuid = res_ops.query_resource(res_ops.BACKUP_STORAGE)[0].uuid
    print bs_uuid

    test_stub.reload_default_license()
    test_util.test_logger('Check default community license')
    test_stub.check_license(None, None, 2147483647, False, 'Community')


    test_util.test_pass('Check License Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
