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

def test():
    test_stub.reload_default_license()
    test_util.test_logger('Check default community license')
    test_stub.check_license(None, None, 2147483647, False, 'Community')

    test_util.test_logger('Load and Check TrialExt license with 5 day and 5 HOST')
    file_path = test_stub.gen_license('woodpecker', 'woodpecker@zstack.io', '5', 'HybridTrialExt', '', '5')
    test_stub.load_license(file_path)
    test_stub.check_license("woodpecker@zstack.io", None, 5, False, 'HybridTrialExt')

    # add the vcenter 1.203
    username = os.environ.get("vcenteruser")
    pasword = os.environ.get("vcenterpwd")
    zone_name = os.environ.get("zoneName")
    conditions = res_ops.gen_query_conditions('name', '=', zone_name)
    zone_uuid = res_ops.query_resource(res_ops.ZONE, conditions)[0].uuid

    vct_ops.add_vcenter("vcenter_test", "172.20.1.203", username, password, https, zone_uuid)   

    test_util.test_pass('Check License Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
