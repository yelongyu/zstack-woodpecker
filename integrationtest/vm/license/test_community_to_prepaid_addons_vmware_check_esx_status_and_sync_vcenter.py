'''

New Integration Test for License.

@author: ye.tian 20190610
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

    # add the vcenter 1.50

    test_stub.create_zone()
    username = os.environ.get("vcenteruser")
    password = os.environ.get("vcenterpwd")
    zone_name = "ZONE1"
    conditions = res_ops.gen_query_conditions('name', '=', zone_name)
    zone_uuid = res_ops.query_resource(res_ops.ZONE, conditions)[0].uuid
    https = "true"
    vcenterdomain = "172.20.0.50"
    try:
        vct_ops.add_vcenter("vcenter_test", vcenterdomain, username, password, https, zone_uuid)
        test_util.test_fail('vCenter can not add success')
    except Exception:
	pass

    test_util.test_logger('load and check addon license vmware with 2 day and 1 CPU ')
    file_path = test_stub.gen_addons_license('woodpecker', 'woodpecker@zstack.io', '2', 'Addon', '1', '', 'vmware')
    node_uuid = res_ops.query_resource(res_ops.MANAGEMENT_NODE)[0].uuid
    test_stub.update_license(node_uuid, file_path)
    issued_date = test_stub.get_license_addons_info().issuedDate
    expired_date = test_stub.license_date_cal(issued_date, 86400 * 2)
    test_stub.check_license_addons(1, None, False, 'AddOn', issued_date=issued_date, expired_date=expired_date)
    
    vct_ops.add_vcenter("vcenter_test", vcenterdomain, username, password, https, zone_uuid)

    vcenter_uuid = res_ops.get_resource(res_ops.VCENTER)[0].uuid
    # sync vcenter
    time.sleep(10)
    esx_name = '172.20.1.111'
    conditions1 = res_ops.gen_query_conditions('name', '=', esx_name)
    esx_status = res_ops.query_resource(res_ops.HOST, conditions1)[0].status
    if esx_status != 'Connected':
        test_util.test_fail('the esx host status is %s,test fail' % esx_status)
    else:
        test_util.test_logger('the esx host status is Connected, continue')

    vct_ops.sync_vcenter(vcenter_uuid)

    time.sleep(15)
    vct_ops.delete_vcenter(vcenter_uuid)

    time.sleep(5)
    zone_ops.delete_zone(zone_uuid)

    test_util.test_logger('start to delete the addons vmware license')
    uuid = test_stub.get_license_addons_info().uuid
    lic_ops.delete_license(node_uuid, uuid)
    test_util.test_logger('delete the addons license [uuid:] %s' % uuid)


    test_util.test_pass('Check License and add the vcenter  and check sync Test Success')


#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
