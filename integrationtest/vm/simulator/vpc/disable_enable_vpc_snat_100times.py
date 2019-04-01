'''

New Simulator Test for VPC SNAT

@author: Hengguo Ge
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.vpc_operations as vpc_ops
import os

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()



vpc_l3_name = 'l3VpcNetwork1'
vpc_vr_name = 'vpc1'


def test():
    if "test-config-vpc-dns.xml" != os.path.basename(os.environ.get('WOODPECKER_TEST_CONFIG_FILE')).strip():
        test_util.test_skip('Skip test on test config except test-config-vpc-dns.xml')

    test_util.test_dsc("1. create vpc vrouter")
    vr = test_stub.create_vpc_vrouter(vpc_vr_name)
    vr_uuid = vr.inv.uuid

    vpc_l3_uuid = test_lib.lib_get_l3_by_name(vpc_l3_name).uuid

    test_util.test_dsc("2. attach vpc network to vpc router")
    test_stub.attach_l3_to_vpc_vr_by_uuid(vr, vpc_l3_uuid)

    test_util.test_dsc("3. disable and enable vpc snat service for 100 times")
    for i in range(1,100):
        vpc_ops.set_vpc_vrouter_network_service_state(vr_uuid, networkService='SNAT', state='disable')
        vpc_ops.set_vpc_vrouter_network_service_state(vr_uuid, networkService='SNAT', state='enable')

    serviceState = vpc_ops.get_vpc_vrouter_network_service_state(vr_uuid, networkService='SNAT')
    if serviceState.env.state != 'enable':
        test_util.test_fail("enable SNAT failed.")

    test_util.test_dsc("4. enable and disable vpc snat service for 100 times")
    for i in range(1,100):
        vpc_ops.set_vpc_vrouter_network_service_state(vr_uuid, networkService='SNAT', state='enable')
        vpc_ops.set_vpc_vrouter_network_service_state(vr_uuid, networkService='SNAT', state='disable')

    serviceState = vpc_ops.get_vpc_vrouter_network_service_state(vr_uuid, networkService='SNAT')
    if serviceState.env.state != 'disable':
        test_util.test_fail("disable SNAT failed.")

def env_recover():
    test_lib.lib_error_cleanup(test_obj_dict)
    test_stub.remove_all_vpc_vrouter()