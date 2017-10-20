'''
@author: FangSun
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.vm_operations as vm_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.net_operations as net_ops
import time
import random
import os
from itertools import izip



test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()


all_vpc_l3_list = ['l3VlanNetworkName1'] + ["l3VlanNetwork{}".format(i) for i in xrange(2,11)] + \
                  ["l3VxlanNetwork{}".format(i) for i in xrange(11,21)]


@test_lib.pre_execution_action(test_stub.remove_all_vpc_vrouter)
def test():

    test_util.test_dsc("create vpc vrouter and attach vpc l3 to vpc")

    vr_inv = test_stub.create_vpc_vrouter()

    for _ in xrange(5):
        test_stub.attach_all_l3_to_vpc_vr(vr_inv, all_vpc_l3_list)

        conf = res_ops.gen_query_conditions('uuid', '=', vr_inv.uuid)
        vr_inv = res_ops.query_resource(res_ops.VM_INSTANCE, conf)[0]
        nic_uuid_list = [nic.uuid for nic in vr_inv.vmNics if nic.metaData == '4']
        assert len(nic_uuid_list) == len(all_vpc_l3_list)

        for nic_uuid in nic_uuid_list:
            net_ops.detach_l3(nic_uuid)

        time.sleep(10)

    test_stub.remove_all_vpc_vrouter()

def env_recover():
    test_stub.remove_all_vpc_vrouter()
    test_lib.lib_error_cleanup(test_obj_dict)

