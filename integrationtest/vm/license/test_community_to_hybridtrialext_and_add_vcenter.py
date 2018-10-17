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

    test_util.test_logger('Load and Check TrialExt license with 5 day and 5 HOST')
    file_path = test_stub.gen_license('woodpecker', 'woodpecker@zstack.io', '5', 'HybridTrialExt', '', '5')
    test_stub.load_license(file_path)
    test_stub.check_license("woodpecker@zstack.io", None, 5, False, 'HybridTrialExt')

    # add the vcenter 1.203
    test_stub.create_zone()
    username = os.environ.get("vcenteruser")
    password = os.environ.get("vcenterpwd")
    zone_name = "ZONE1"
    conditions = res_ops.gen_query_conditions('name', '=', zone_name)
    zone_uuid = res_ops.query_resource(res_ops.ZONE, conditions)[0].uuid
    https = "true"
    vcenterdomain = "172.20.1.203"
    vct_ops.add_vcenter("vcenter_test", vcenterdomain, username, password, https, zone_uuid)
    vcenter_uuid = res_ops.get_resource(res_ops.VCENTER)[0].uuid
    time.sleep(5)
    vct_ops.delete_vcenter(vcenter_uuid)

    time.sleep(5)
    zone_ops.delete_zone(zone_uuid)

    node_uuid = res_ops.query_resource(res_ops.MANAGEMENT_NODE)[0].uuid
    test_util.test_logger('start to delete the license')
    uuid = test_stub.get_license_info().uuid
    lic_ops.delete_license(node_uuid, uuid)
    test_util.test_logger('delete the license [uuid:] %s' % uuid)

    test_util.test_pass('Check License and add/del vcenter Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
