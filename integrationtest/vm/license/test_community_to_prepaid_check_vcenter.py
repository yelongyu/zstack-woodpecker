'''

New Integration Test for License.

@author: ye.tian 20181005
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.license_operations as lic_ops
import zstackwoodpecker.operations.vcenter_operations as vct_ops
import zstackwoodpecker.operations.zone_operations as zone_ops
import time
import datetime
import os

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def test():
    test_stub.reload_default_license()
    test_util.test_logger('Check default community license')
    test_stub.check_license(None, None, 2147483647, False, 'Community')

    test_util.test_logger('Load and Check TrialExt license with 10 day and 1 CPU')
    file_path = test_stub.gen_license('woodpecker', 'woodpecker@zstack.io', '10', 'Prepaid', '1', '')
    test_stub.load_license(file_path)
    issued_date = test_stub.get_license_info().issuedDate
    expired_date = test_stub.license_date_cal(issued_date, 86400 * 10)
    test_stub.check_license("woodpecker@zstack.io", 1, None, False, 'Paid', issued_date=issued_date, expired_date=expired_date)

    # add the vcenter 1.203

    test_stub.create_zone()
    username = os.environ.get("vcenteruser")
    password = os.environ.get("vcenterpwd")
    zone_name = "ZONE1"
    conditions = res_ops.gen_query_conditions('name', '=', zone_name)
    zone_uuid = res_ops.query_resource(res_ops.ZONE, conditions)[0].uuid
    https = "true"
    vcenterdomain = "172.20.0.50"
    vct_ops.add_vcenter("vcenter_test", vcenterdomain, username, password, https, zone_uuid)
    vcenter_uuid = res_ops.get_resource(res_ops.VCENTER)[0].uuid
    time.sleep(5)
    vct_ops.delete_vcenter(vcenter_uuid)

    time.sleep(5)
    zone_ops.delete_zone(zone_uuid)

    test_util.test_pass('Check License and add the vcenter Test Success')


#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
