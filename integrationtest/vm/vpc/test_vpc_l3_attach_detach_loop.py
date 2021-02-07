'''
@author: FangSun
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.net_operations as net_ops
import time
import random
import os

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()


case_flavor = dict(one_vpc=   dict(vpc_num=1),
                   two_vpc=   dict(vpc_num=2),
                   )

vr_list = []


@test_lib.pre_execution_action(test_stub.remove_all_vpc_vrouter)
def test():
    flavor = case_flavor[os.environ.get('CASE_FLAVOR')]
    test_util.test_dsc("create vpc vrouter and attach vpc l3 to vpc")
    vr_list.append(test_stub.create_vpc_vrouter('vpc1'))
    if flavor['vpc_num'] == 2:
        vr_list.append(test_stub.create_vpc_vrouter('vpc2'))

    ROUND = 2 if flavor['vpc_num'] == 1 else 1

    for _ in xrange(ROUND):
        for vr in vr_list:
            test_stub.attach_l3_to_vpc_vr(vr, test_stub.all_vpc_l3_list)
            nic_uuid_list = [nic.uuid for nic in vr.inv.vmNics if nic.metaData in ['4', '8']]
            assert len(nic_uuid_list) == len(test_stub.all_vpc_l3_list)
            [vr.remove_nic(nic_uuid) for nic_uuid in nic_uuid_list]

    test_lib.lib_error_cleanup(test_obj_dict)
    test_stub.remove_all_vpc_vrouter()

def env_recover():
    test_lib.lib_error_cleanup(test_obj_dict)
    test_stub.remove_all_vpc_vrouter()

