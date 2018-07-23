'''

New Simulator Test for VPC DNS

@author: Hengguo Ge
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.vpcdns_operations as vpcdns_ops
import os

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

'''
steps:
1. create vpc router.  

2. add dns to vpc router  

3. get vpc dns list and check.   

'''

vpc_vr_name = 'vpc1'
dns_list = ['223.5.5.5', '1.1.1.1', '4.2.2.2', '8.8.8.8']
vpc_dns_list = []


def test():
    if "test-config-vpc-dns.xml" != os.path.basename(os.environ.get('WOODPECKER_TEST_CONFIG_FILE')).strip():
        test_util.test_skip('Skip test on test config except test-config-vpc-dns.xml')
    test_util.test_dsc("1. create vpc vrouter")
    vr = test_stub.create_vpc_vrouter(vpc_vr_name)
    vr_uuid = vr.inv.uuid

    test_util.test_dsc("2. add dns vpc router")
    for dns in dns_list:
        vpcdns_ops.add_dns_to_vpc_router(vr_uuid, dns)

    test_util.test_dsc("3. get vpc dns list and check")
    vpc_dns_info = test_stub.query_vpc_vrouter(vpc_vr_name).inv.dns
    for vpc_dns in vpc_dns_info:
        vpc_dns_list.append(vpc_dns['dns'])

    if vpc_dns_list != dns_list:
        test_util.test_fail("add dns to vpc router failed.")
    else:
        for dns in dns_list:
            vpcdns_ops.remove_dns_from_vpc_router(vr_uuid, dns)
        test_util.test_pass("add dns to vpc router passed.")


def env_recover():
    test_lib.lib_error_cleanup(test_obj_dict)
    test_stub.remove_all_vpc_vrouter()