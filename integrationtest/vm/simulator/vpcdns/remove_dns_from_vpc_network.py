'''

New Simulator Test for VPC DNS

@author: Hengguo Ge
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.vpcdns_operations as vpcdns_ops

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

'''
steps:
1. create vpc router.  

2. create vpc network and attach vpc network to vpc router.

3. add dns to vpc network and vpc router

4. remove dns from vpc network.   

5. get vpc dns list and check.   

'''

vpc_l3_name = 'l3VpcNetwork1'
vpc_vr_name = 'vpc1'
default_dns = '223.5.5.5'
vpc_dns_list_begin = ['223.5.5.5']
l3_dns_list = ['1.1.1.1', '8.8.8.8']
vpc_dns_list_end = []
vr_uuid_list = []


def test():
    test_util.test_dsc("1. create vpc vrouter")
    vr = test_stub.create_vpc_vrouter(vpc_vr_name)
    vr_uuid = vr.inv.uuid

    test_util.test_dsc("2. attach vpc network to vpc router")
    vpc_l3_uuid = test_lib.lib_get_l3_by_name(vpc_l3_name).uuid
    test_stub.attach_l3_to_vpc_vr_by_uuid(vr, vpc_l3_uuid)

    test_util.test_dsc("3. add dns to vpc network and vpc router")
    for dns in l3_dns_list:
        vpcdns_ops.add_dns_to_l3_network(vpc_l3_uuid, dns)

    vpcdns_ops.add_dns_to_vpc_router(vr_uuid, default_dns)

    test_util.test_dsc("4. remove dns from vpc network")
    for dns in l3_dns_list:
        vpcdns_ops.remove_dns_from_l3_network(vpc_l3_uuid, dns)

    test_util.test_dsc("5. get vpc dns list and check")
    vpc_dns_info = test_stub.query_vpc_vrouter(vpc_vr_name).inv.dns
    for vpc_dns in vpc_dns_info:
        vpc_dns_list_end.append(vpc_dns['dns'])

    if vpc_dns_list_end != vpc_dns_list_begin:
        test_util.test_fail("remove dns from vpc network take effect on vpc router, not expected.")
    else:
        test_util.test_pass("remove dns from vpc network take no effect on vpc router, expected.")


def env_recover():
    test_lib.lib_error_cleanup(test_obj_dict)
    test_stub.remove_all_vpc_vrouter()